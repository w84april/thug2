// Export address metadata only; never modify the analysis database.
// Run with -process THUG2.exe -noanalysis -readOnly.
// @category THUG2
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.listing.Function;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;

public class ExportFunctionRanges extends GhidraScript {
    public void run() throws Exception {
        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(Paths.get(getScriptArgs()[0])))) {
            out.println("address\tbody_bytes\tranges");
            for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                monitor.checkCancelled();
                StringBuilder ranges = new StringBuilder();
                for (AddressRange range : f.getBody().getAddressRanges()) {
                    if (ranges.length() != 0) ranges.append(';');
                    ranges.append(range.getMinAddress()).append(':').append(range.getMaxAddress());
                }
                out.printf("%s\t%d\t%s%n", f.getEntryPoint(), f.getBody().getNumAddresses(), ranges);
            }
        }
    }
}
