use objdiff_core::bindings::report::Report;
use objdiff_core::bindings::report::Measures;

fn no_matching(m: &Measures) -> Result<(), Box<dyn std::error::Error>> {
    if m.matched_code != 0 || m.matched_data != 0 || m.matched_functions != 0
        || m.matched_code_percent != 0.0 || m.matched_data_percent != 0.0
        || m.matched_functions_percent != 0.0 || m.fuzzy_match_percent != 0.0
        || m.total_data != 0 || m.complete_data != 0 || m.complete_data_percent != 0.0 {
        return Err("This recovery has no verified binary matches or data completion".into());
    }
    if m.complete_code > m.total_code { return Err("Completion exceeds denominator".into()); }
    let percent = if m.total_code == 0 { 0.0 } else {
        m.complete_code as f64 / m.total_code as f64 * 100.0
    };
    if !m.complete_code_percent.is_finite() || (m.complete_code_percent as f64 - percent).abs() > 0.0001 {
        return Err("Incorrect completion percentage".into());
    }
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args().nth(1).ok_or("Usage: progress-validator report.json")?;
    let mut report = Report::parse(&std::fs::read(path)?)?;
    if report.version != 2 { return Err("Expected objdiff report v2".into()); }
    report.migrate()?;
    let measures = report.measures.as_ref().ok_or("Missing aggregate measures")?;
    no_matching(measures)?;
    let mut sum = Measures::default();
    for unit in &report.units {
        let m = unit.measures.as_ref().ok_or("Missing unit measures")?;
        no_matching(m)?;
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
        if unit.functions.iter().chain(unit.sections.iter()).any(|f| f.fuzzy_match_percent != 0.0) {
            return Err("Item contains unverified binary-match credit".into());
        }
        sum += *m;
    }
    if (sum.total_code, sum.complete_code, sum.total_functions, sum.total_units, sum.complete_units)
        != (measures.total_code, measures.complete_code, measures.total_functions, measures.total_units, measures.complete_units) {
        return Err("Aggregate differs from unit totals".into());
    }
    for category in &report.categories {
        no_matching(category.measures.as_ref().ok_or("Missing category measures")?)?;
    }
    println!("objdiff v{}: {} units, {} functions, {} complete / {} total bytes; zero binary matches",
        report.version, report.units.len(), measures.total_functions, measures.complete_code, measures.total_code);
    Ok(())
}
