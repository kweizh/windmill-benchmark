import { step, workflow } from "windmill-client";

export const main = workflow("wac_step_determinism", async () => {
	const capturedTimestamp = await step("init_time", () => new Date().toISOString());

	// Derive YYYY-MM-DD from the captured timestamp (first 10 characters)
	const datePortion = capturedTimestamp.slice(0, 10);

	return {
		capturedTimestamp,
		datePortion,
	};
});
