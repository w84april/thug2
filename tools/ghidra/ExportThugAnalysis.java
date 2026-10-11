// Import evidence-based names and export function/call indexes plus selected pseudocode.
// Generated pseudocode is analysis material, NOT buildable recovered source.
// @category THUG2
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import java.nio.file.*;
import java.io.*;
import java.util.*;

public class ExportThugAnalysis extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        Path out = Paths.get(args[0]);
        Files.createDirectories(out.resolve("pseudocode"));
        for (String line : Files.readAllLines(Paths.get(args[1]))) {
            String[] parts = line.split("\t");
            Address address = toAddr(Long.parseLong(parts[0], 16));
            Function function = getFunctionAt(address);
            if (function == null) { disassemble(address); function = createFunction(address, parts[1]); }
            if (function != null) function.setName(parts[1], SourceType.USER_DEFINED);
        }
        Set<Function> focus = new LinkedHashSet<>();
        List<Long> roots = new ArrayList<>(Arrays.asList(0x401aa0L,0x401af0L,0x401b30L,0x401b90L,0x401be0L,
                        0x445130L,0x445320L,0x565260L,0x5654b0L,0x5654d0L,
                        0x46fba0L,0x5b7c00L,0x5b7290L));
        for (int i = 2; i < args.length; i++) roots.add(Long.parseLong(args[i], 16));
        for (long a : roots) {
            Function f = getFunctionAt(toAddr(a));
            if (f != null) {
                focus.add(f);
                focus.addAll(f.getCalledFunctions(monitor));
            }
        }
        try (PrintWriter index = new PrintWriter(Files.newBufferedWriter(out.resolve("functions.tsv")));
             PrintWriter calls = new PrintWriter(Files.newBufferedWriter(out.resolve("calls.tsv")))) {
            index.println("address\tname\tbody_bytes\tprototype");
            calls.println("caller\tcallee");
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function f = functions.next();
                index.printf("%s\t%s\t%d\t%s%n",f.getEntryPoint(),f.getName(),
                             f.getBody().getNumAddresses(),f.getPrototypeString(false,false));
                for (Function callee : f.getCalledFunctions(monitor))
                    calls.printf("%s\t%s%n",f.getEntryPoint(),callee.getEntryPoint());
            }
        }
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        int success = 0;
        try (PrintWriter status = new PrintWriter(Files.newBufferedWriter(out.resolve("decompilation.tsv")))) {
            status.println("address\tname\tstatus");
            for (Function f : focus) {
                monitor.checkCancelled();
                DecompileResults result = decompiler.decompileFunction(f,60,monitor);
                String state = result.decompileCompleted() ? "pseudocode_only" : result.getErrorMessage().replace('\n',' ');
                status.printf("%s\t%s\t%s%n",f.getEntryPoint(),f.getName(),state);
                status.flush();
                if (result.decompileCompleted()) {
                    Files.writeString(out.resolve("pseudocode").resolve(f.getEntryPoint()+"_"+f.getName()+".c"),
                        "/* GENERATED ANALYSIS: not validated or buildable recovered source. */\n"+
                        result.getDecompiledFunction().getC());
                    success++;
                }
            }
        }
        decompiler.dispose();
        println("THUG2: exported " + success + " focused pseudocode functions out of " + focus.size());
    }
}
