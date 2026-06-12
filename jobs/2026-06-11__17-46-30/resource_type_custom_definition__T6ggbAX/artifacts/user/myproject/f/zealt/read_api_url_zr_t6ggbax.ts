import * as wmill from "windmill-client";

export async function main(): Promise<string> {
  const resource = await wmill.getResource("f/zealt/creds_zr_t6ggbax");
  return resource.apiUrl as string;
}
