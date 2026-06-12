import * as wmill from "windmill-client";

export async function main() {
  const resource = await wmill.getResource("f/zealt/creds_zr_etkgdhj");
  return resource.apiUrl;
}
