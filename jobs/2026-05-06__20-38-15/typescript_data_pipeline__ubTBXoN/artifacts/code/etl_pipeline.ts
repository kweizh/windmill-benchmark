export async function main(
  raw_records: Array<{ name: string; value: string; category: string }>,
  filter_category: string = "",
  value_multiplier: number = 1
) {
  const input_count = raw_records.length;
  let parse_errors = 0;

  // 1. Parse: convert value from string to float
  const parsed_data = raw_records.map((record) => {
    const floatValue = parseFloat(record.value);
    if (isNaN(floatValue)) {
      parse_errors++;
      return { ...record, value: NaN, parse_error: true };
    }
    return { ...record, value: floatValue, parse_error: false };
  });

  // Filter out records where value is not a valid number for subsequent stages
  let pipeline_records = parsed_data
    .filter((r) => !r.parse_error)
    .map((r) => ({
      name: r.name,
      value: r.value as number,
      category: r.category,
    }));

  // 2. Filter: if filter_category is non-empty, keep only records where category === filter_category
  if (filter_category !== "") {
    pipeline_records = pipeline_records.filter(
      (r) => r.category === filter_category
    );
  }

  // 3. Transform: multiply each numeric value by value_multiplier
  const transformed_records = pipeline_records.map((r) => ({
    ...r,
    value: r.value * value_multiplier,
  }));

  // 4. Aggregate: compute { total: sum, count, average } from the transformed values
  const total = transformed_records.reduce((acc, r) => acc + r.value, 0);
  const count = transformed_records.length;
  const average = count > 0 ? total / count : 0;

  return {
    input_count,
    output_count: count,
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
