// Multi-stage ETL pipeline: parse, filter, transform, aggregate

type RawRecord = {
  name: string;
  value: string;
  category: string;
};

type ParsedRecord = {
  name: string;
  value: number;
  category: string;
  parse_error?: boolean;
};

type OutputRecord = {
  name: string;
  value: number;
  category: string;
};

type Aggregate = {
  total: number;
  count: number;
  average: number;
};

type PipelineResult = {
  input_count: number;
  output_count: number;
  parse_errors: number;
  filter_category: string;
  records: OutputRecord[];
  aggregate: Aggregate;
};

// Stage 1: Parse — convert value from string to float, flag invalid records
function stageParseRecords(raw: RawRecord[]): ParsedRecord[] {
  return raw.map((record) => {
    const parsed = parseFloat(record.value);
    if (isNaN(parsed)) {
      return { name: record.name, value: 0, category: record.category, parse_error: true };
    }
    return { name: record.name, value: parsed, category: record.category };
  });
}

// Stage 2: Filter — keep only records matching the given category (if specified)
function stageFilterRecords(records: ParsedRecord[], filterCategory: string): ParsedRecord[] {
  if (!filterCategory) {
    return records;
  }
  return records.filter((record) => record.category === filterCategory);
}

// Stage 3: Transform — multiply each record's value by the given multiplier
function stageTransformRecords(records: ParsedRecord[], multiplier: number): OutputRecord[] {
  return records.map((record) => ({
    name: record.name,
    value: record.value * multiplier,
    category: record.category,
  }));
}

// Stage 4: Aggregate — compute total, count, and average from transformed values
function stageAggregateRecords(records: OutputRecord[]): Aggregate {
  const count = records.length;
  if (count === 0) {
    return { total: 0, count: 0, average: 0 };
  }
  const total = records.reduce((sum, record) => sum + record.value, 0);
  const average = total / count;
  return { total, count, average };
}

export async function main(
  raw_records: Array<{ name: string; value: string; category: string }>,
  filter_category: string = "",
  value_multiplier: number = 1
): Promise<PipelineResult> {
  const inputCount = raw_records.length;

  // Stage 1: Parse
  const parsedRecords = stageParseRecords(raw_records);
  const parseErrors = parsedRecords.filter((r) => r.parse_error === true).length;

  // Exclude records with parse errors from subsequent stages
  const validRecords = parsedRecords.filter((r) => !r.parse_error);

  // Stage 2: Filter
  const filteredRecords = stageFilterRecords(validRecords, filter_category);

  // Stage 3: Transform
  const transformedRecords = stageTransformRecords(filteredRecords, value_multiplier);

  // Stage 4: Aggregate
  const aggregate = stageAggregateRecords(transformedRecords);

  return {
    input_count: inputCount,
    output_count: transformedRecords.length,
    parse_errors: parseErrors,
    filter_category: filter_category,
    records: transformedRecords,
    aggregate,
  };
}
