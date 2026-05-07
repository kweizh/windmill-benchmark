export async function main(should_fail: boolean = false) {
  if (should_fail) {
    throw new Error("Intentional failure for testing");
  }
  return { status: "ok", message: "Operation completed successfully" };
}