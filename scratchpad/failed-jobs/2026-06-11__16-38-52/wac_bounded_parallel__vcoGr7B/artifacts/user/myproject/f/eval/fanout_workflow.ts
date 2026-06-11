import { workflow, task, parallel } from 'windmill-client';

async function httpGet(url: string): Promise<{ url: string; status: number }> {
	const response = await fetch(url);
	return { url, status: response.status };
}

export const main = workflow(async (urls: string[]) => {
	const results = await parallel(
		urls,
		(url: string) => task(httpGet)(url),
		{ concurrency: 3 }
	);
	return results;
});
