import { step, workflow } from "windmill-client";

export const main = workflow(async () => {
    const capturedTimestamp = await step("init_time", async () => {
        return new Date().toISOString();
    });

    const downstreamValue = capturedTimestamp.substring(0, 10);

    return {
        timestamp: capturedTimestamp,
        derived: downstreamValue
    };
});
