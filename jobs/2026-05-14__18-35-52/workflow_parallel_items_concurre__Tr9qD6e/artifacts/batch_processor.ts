import { parallel, task, workflow } from "windmill-client";

type UrlCheckResult = {
  url: string;
  status: number;
  ok: boolean;
};

type SummaryResult = {
  total: number;
  successful: number;
  failed: number;
};

const checkUrl = async (url: string): Promise<UrlCheckResult> => {
  try {
    const response = await fetch(url);

    return {
      url,
      status: response.status,
      ok: response.ok,
    };
  } catch (error) {
    return {
      url,
      status: 0,
      ok: false,
    };
  }
};

const summarize = async (results: UrlCheckResult[]): Promise<SummaryResult> => {
  const successful = results.filter((result) => result.ok).length;

  return {
    total: results.length,
    successful,
    failed: results.length - successful,
  };
};

export const main = workflow(async (urls: string[]) => {
  const results = await parallel(urls, (url) => task(checkUrl)(url), {
    concurrency: 3,
  });

  return task(summarize)(results);
});
