import { task, workflow } from 'windmill-client';

async function fetchSectionData(section: string): Promise<{ section: string; data: string; timestamp: string }> {
  return {
    section,
    data: `Data for ${section}`,
    timestamp: new Date().toISOString(),
  };
}

async function compileReport(sections: any[]): Promise<{ title: string; sections: number; content: any[] }> {
  return {
    title: 'Weekly Report',
    sections: sections.length,
    content: sections,
  };
}

export const main = workflow(async () => {
  const [summary, details, metrics] = await Promise.all([
    task(fetchSectionData)('summary'),
    task(fetchSectionData)('details'),
    task(fetchSectionData)('metrics'),
  ]);

  const sections = [summary, details, metrics];
  const report = await task(compileReport)(sections);
  return report;
});