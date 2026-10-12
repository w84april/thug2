// Discover supplied recovery entry points in a read-only session. Ghidra discards
// these in-memory changes; the existing project and earlier exports stay intact.
// @category THUG2
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.listing.Function;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;

public class ExportAdditionalFunctionRanges extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(Paths.get(args[1])))) {
            out.println("address\tbody_bytes\tranges");
            for (String entry : Files.readAllLines(Paths.get(args[0]))) {
                monitor.checkCancelled();
                if (entry.isBlank()) continue;
                var address = toAddr(Long.parseLong(entry, 16));
                Function f = getFunctionAt(address);
                if (f == null) { disassemble(address); f = createFunction(address, null); }
                if (f == null) { println("Unresolved entry " + entry); continue; }
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
