#!/usr/bin/env node

import { createPublicKey, verify } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const keyID = "swiftps2-release-1";
const repositoryRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const encodedKey = readFileSync(join(repositoryRoot, "keys", `${keyID}.pub`), "utf8").trim();
const rawKey = Buffer.from(encodedKey, "base64");
if (rawKey.length !== 32 || rawKey.toString("base64") !== encodedKey) {
    throw new Error(`${keyID} must be one canonical raw 32-byte Ed25519 public key`);
}
const subjectPublicKeyInfo = Buffer.concat([
    Buffer.from("302a300506032b6570032100", "hex"),
    rawKey,
]);
const publicKey = createPublicKey({
    key: subjectPublicKeyInfo,
    format: "der",
    type: "spki",
});

for (const channel of ["stable", "preview"]) {
    const document = readFileSync(join(repositoryRoot, "channels", `${channel}.json`));
    const signatureText = readFileSync(
        join(repositoryRoot, "channels", `${channel}.json.sig`),
        "utf8"
    ).trim();
    const signature = Buffer.from(signatureText, "base64");
    if (signature.length !== 64 || signature.toString("base64") !== signatureText) {
        throw new Error(`${channel} signature is not canonical Ed25519 base64`);
    }
    const metadata = JSON.parse(document.toString("utf8"));
    if (metadata.signingKeyID !== keyID) {
        throw new Error(`${channel} channel names an unexpected signing key`);
    }
    if (!verify(null, document, publicKey, signature)) {
        throw new Error(`${channel} channel signature is invalid`);
    }
}
