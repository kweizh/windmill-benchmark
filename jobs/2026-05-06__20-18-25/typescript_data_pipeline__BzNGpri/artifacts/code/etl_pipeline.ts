export async function main(
  raw_records: Array<{ name: string; value: string; category: string }>,
  filter_category: string = "",
  value_multiplier: number = 1
) {
  const input_count = raw_records.length;
  let parse_errors = 0;

  // Stage 1: Parse - convert value from string to float
  const parsed_records = raw_records.map((record) => {
    const parsed_value = parseFloat(record.value);
    if (isNaN(parsed_value)) {
      parse_errors++;
      return { ...record, parse_error: true };
    }
    return { ...record, value: parsed_value, parse_error: false };
  });

  // Stage 2: Filter - keep only records without parse errors and matching category
  const filtered_records = parsed_records.filter((record) => {
    if (record.parse_error) return false;
    if (filter_category !== "" && record.category !== filter_category)
      return false;
    return true;
  });

  // Stage 3: Transform - multiply each numeric value by value_multiplier
  const transformed_records = filtered_records.map((record) => ({
    name: record.name,
    value: (record.value as number) * value_multiplier,
    category: record.category,
  }));

  // Stage 4: Aggregate - compute total, count, average
  const output_count = transformed_records.length;
  const total = transformed_records.reduce(
    (sum, record) => sum + record.value,
    0
  );
  const count = output_count;
  const average = count > 0 ? total / count : 0;

  return {
    input_count,
    output_count,
    parse_errors,
    filter_category,
    records: transformed_records,
    aggregate: {
      total,
      count,
      average,
    },
  };
}