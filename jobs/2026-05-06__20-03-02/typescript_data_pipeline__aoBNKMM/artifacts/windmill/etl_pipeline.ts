type RawRecord = {
  name: string;
  value: string;
  category: string;
};

type ParsedRecord = {
  name: string;
  value: number;
  category: string;
};

type ParsedResult = {
  records: ParsedRecord[];
  parseErrors: number;
};

const parseRecords = (rawRecords: RawRecord[]): ParsedResult => {
  const records: ParsedRecord[] = [];
  let parseErrors = 0;

  for (const record of rawRecords) {
    const parsedValue = Number.parseFloat(record.value);
    if (Number.isNaN(parsedValue)) {
      parseErrors += 1;
      continue;
    }

    records.push({
      name: record.name,
      value: parsedValue,
      category: record.category,
    });
  }

  return { records, parseErrors };
};

const filterRecords = (
  records: ParsedRecord[],
  filterCategory: string,
): ParsedRecord[] => {
  if (!filterCategory) {
    return records;
  }

  return records.filter((record) => record.category === filterCategory);
};

const transformRecords = (
  records: ParsedRecord[],
  valueMultiplier: number,
): ParsedRecord[] =>
  records.map((record) => ({
    ...record,
    value: record.value * valueMultiplier,
  }));

const aggregateRecords = (records: ParsedRecord[]) => {
  const total = records.reduce((sum, record) => sum + record.value, 0);
  const count = records.length;
  const average = count === 0 ? 0 : total / count;

  return { total, count, average };
};

export async function main(
  raw_records: Array<{ name: string; value: string; category: string }>,
  filter_category: string = "",
  value_multiplier: number = 1,
) {
  const inputCount = raw_records.length;

  const parsed = parseRecords(raw_records);
  const filtered = filterRecords(parsed.records, filter_category);
  const transformed = transformRecords(filtered, value_multiplier);
  const aggregate = aggregateRecords(transformed);

  return {
    input_count: inputCount,
    output_count: transformed.length,
    parse_errors: parsed.parseErrors,
    filter_category,
    records: transformed,
    aggregate,
  };
}
