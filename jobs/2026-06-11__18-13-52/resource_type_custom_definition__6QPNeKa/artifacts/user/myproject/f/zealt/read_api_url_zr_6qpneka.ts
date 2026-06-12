import * as wmill from "windmill-client";

export async function main() {
  const res = await wmill.getResource("f/zealt/creds_zr_6qpneka");
  return res.apiUrl;
}
