use objdiff_core::bindings::report::Report;
use objdiff_core::bindings::report::Measures;

fn valid_measures(m: &Measures) -> Result<(), Box<dyn std::error::Error>> {
    if m.matched_data != 0 || m.matched_data_percent != 0.0
        || m.total_data != 0 || m.complete_data != 0 || m.complete_data_percent != 0.0 {
        return Err("This recovery has no verified data matching or completion".into());
    }
    // Matching and original-target linked accounting are independent in objdiff.
    if m.complete_code > m.total_code || m.matched_code > m.total_code
        || m.matched_functions > m.total_functions {
        return Err("Completion/matching exceeds verified bounds".into());
    }
    if m.complete_code != 0 || m.complete_units != 0 {
        return Err("No original-target linked-unit evidence is selected".into());
    }
    for (actual, numerator, denominator) in [
        (m.complete_code_percent, m.complete_code, m.total_code),
        (m.matched_code_percent, m.matched_code, m.total_code),
        (m.fuzzy_match_percent, m.matched_code, m.total_code),
        (m.matched_functions_percent, m.matched_functions as u64, m.total_functions as u64),
    ] {
        let expected = if denominator == 0 { 0.0 } else { numerator as f64 / denominator as f64 * 100.0 };
        if !actual.is_finite() || (actual as f64 - expected).abs() > 0.0001 {
            return Err("Incorrect completion/matching percentage".into());
        }
    }
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args().nth(1).ok_or("Usage: progress-validator report.json")?;
    let path = std::fs::canonicalize(path)?;
    let mut report = Report::parse(&std::fs::read(&path)?)?;
    if report.version != 2 { return Err("Expected objdiff report v2".into()); }
    report.migrate()?;
    let measures = report.measures.as_ref().ok_or("Missing aggregate measures")?;
    valid_measures(measures)?;
    let mut sum = Measures::default();
    for unit in &report.units {
        let m = unit.measures.as_ref().ok_or("Missing unit measures")?;
        valid_measures(m)?;
        if m.total_functions as usize != unit.functions.len() || m.total_units != 1 {
            return Err("Unit function/unit count differs from contents".into());
        }
        let complete = unit.metadata.as_ref().and_then(|m| m.complete).unwrap_or(false);
        if m.complete_units != complete as u32 || m.complete_code != if complete { m.total_code } else { 0 } {
            return Err("Unit completion differs from metadata".into());
        }
        let size: u64 = unit.functions.iter().map(|f| f.size).sum();
        if size > m.total_code || (m.total_functions > 0 && size != m.total_code) {
            return Err("Original function sizes differ from unit bytes".into());
        }
        if unit.functions.iter().any(|f| f.fuzzy_match_percent != 0.0 && f.fuzzy_match_percent != 100.0)
            || unit.sections.iter().any(|f| f.fuzzy_match_percent != 0.0) {
            return Err("Partial/fuzzy or section matching is unmeasured".into());
        }
        let matched_bytes: u64 = unit.functions.iter().filter(|f| f.fuzzy_match_percent == 100.0).map(|f| f.size).sum();
        let matched_functions = unit.functions.iter().filter(|f| f.fuzzy_match_percent == 100.0).count() as u32;
        if m.matched_code != matched_bytes || m.matched_functions != matched_functions {
            return Err("Unit matching differs from complete exact-match items".into());
        }
        sum += *m;
    }
    if (sum.total_code, sum.complete_code, sum.total_functions, sum.total_units, sum.complete_units, sum.matched_code, sum.matched_functions)
        != (measures.total_code, measures.complete_code, measures.total_functions, measures.total_units, measures.complete_units, measures.matched_code, measures.matched_functions) {
        return Err("Aggregate differs from unit totals".into());
    }
    for category in &report.categories {
        valid_measures(category.measures.as_ref().ok_or("Missing category measures")?)?;
    }
    // Schema parsing and arithmetic cannot establish binary provenance. Require
    // deterministic regeneration against the selected, hashed public evidence.
    // Run from the repository root, including when checking a downloaded artifact.
    let proof_check = std::process::Command::new("python3")
        .args(["tools/generate_progress_report.py", "--check", "--output"])
        .arg(&path).output()?;
    if !proof_check.status.success() {
        return Err(format!("Report differs from validated evidence: {}", String::from_utf8_lossy(&proof_check.stderr)).into());
    }
    println!("objdiff v{}: {} units, {} functions, {} complete / {} total bytes; {} verified native matching bytes",
        report.version, report.units.len(), measures.total_functions, measures.complete_code, measures.total_code, measures.matched_code);
    Ok(())
}
