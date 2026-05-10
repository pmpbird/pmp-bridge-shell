# PMP Vault GitHub Writer Shortcut Build Guide

## Purpose

Build an iPhone Shortcut named exactly:

```text
PMP Vault GitHub Writer
```

This Shortcut is the active no-Cloudflare writer for the PMP Lossless Inventory Vault.

It reads a `PMP_LOSSLESS_VAULT_WRITE_PACKET` from the clipboard, verifies the public-safe privacy gate, and writes `packet.report` to GitHub:

```text
pmp-lossless-inventory-vault/current.json
```

Optional history target:

```text
pmp-lossless-inventory-vault/history/<timestamp>.json
```

## Name boundaries

```text
PMP Vault GitHub Writer
= iPhone Shortcut implementation.

Vault GitHub Writer
= role that writes public-safe Inventory Eyes / Lossless reports to GitHub.

Safe Writer
= separate existing PMP app/code writing tool. Do not confuse it with this Shortcut.
```

## Privacy rule

The Shortcut may write only public-safe app-layer report data.

It must not write:

- private Bug Memory records
- Apple Notes contents
- tokens
- passwords
- secrets
- private localStorage values
- private user data values

Allowed:

- public app file/status metadata
- route/status metadata
- theme/status findings
- privacy-surface flags
- localStorage key names only

## Required private token

Create a GitHub fine-grained token with:

```text
Repository: pmpbird/pmp-bridge-shell
Permissions:
- Contents: Read and write
- Metadata: Read
```

Store the token only inside the private iPhone Shortcut. Never store it in public app HTML, public JavaScript, or any GitHub Pages file.

## Shortcut variables

Use these values in the Shortcut:

```text
GITHUB_OWNER = pmpbird
GITHUB_REPO = pmp-bridge-shell
GITHUB_BRANCH = main
CURRENT_PATH = pmp-lossless-inventory-vault/current.json
GITHUB_TOKEN = <private token stored in Shortcut only>
```

## Shortcut action plan

### 1. Receive packet

Actions:

```text
Get Clipboard
Get Dictionary from Input
Set Variable: Packet
```

### 2. Basic validation

Check these fields from `Packet`:

```text
Packet.type == PMP_LOSSLESS_VAULT_WRITE_PACKET
Packet.writer_name == Vault GitHub Writer
Packet.storage_area == PMP Lossless Inventory Vault
Packet.target_current == pmp-lossless-inventory-vault/current.json
```

If any check fails:

```text
Show Alert: Vault packet failed validation. Do not write.
Stop Shortcut
```

### 3. Privacy gate validation

Get `Packet.privacy_gate` and verify:

```text
private_bug_memory == false
apple_notes_contents == false
tokens == false
passwords == false
secrets == false
private_values == false
localStorage_key_names_only == true
```

If any check fails:

```text
Show Alert: Privacy gate failed. Do not write.
Stop Shortcut
```

### 4. Report validation

Get:

```text
Packet.report
```

Verify:

```text
Packet.report.type == PMP_LOSSLESS_REPORT_WITH_INVENTORY_EYES
```

If not:

```text
Show Alert: Report type failed. Do not write.
Stop Shortcut
```

### 5. Build report text

Actions:

```text
Get Dictionary Value: report from Packet
Text: <Report as JSON>
Base64 Encode Text
Set Variable: Base64Report
```

Important: the GitHub Contents API requires Base64 content.

### 6. Get current file SHA

Request URL:

```text
https://api.github.com/repos/pmpbird/pmp-bridge-shell/contents/pmp-lossless-inventory-vault/current.json?ref=main
```

Action:

```text
Get Contents of URL
Method: GET
Headers:
  Authorization: Bearer <GITHUB_TOKEN>
  Accept: application/vnd.github+json
  X-GitHub-Api-Version: 2022-11-28
```

From the response dictionary, get:

```text
sha
```

Set Variable:

```text
CurrentSHA
```

### 7. Write current.json

Request URL:

```text
https://api.github.com/repos/pmpbird/pmp-bridge-shell/contents/pmp-lossless-inventory-vault/current.json
```

Action:

```text
Get Contents of URL
Method: PUT
Headers:
  Authorization: Bearer <GITHUB_TOKEN>
  Accept: application/vnd.github+json
  X-GitHub-Api-Version: 2022-11-28
  Content-Type: application/json
Request Body: JSON
```

Body:

```json
{
  "message": "PMP Vault GitHub Writer: update current lossless inventory report",
  "branch": "main",
  "content": "Base64Report",
  "sha": "CurrentSHA"
}
```

In Shortcuts, use variables for `Base64Report` and `CurrentSHA`, not the literal words.

### 8. Optional history write

Get:

```text
Packet.target_history
```

If present and starts with:

```text
pmp-lossless-inventory-vault/history/
```

then make another PUT request to:

```text
https://api.github.com/repos/pmpbird/pmp-bridge-shell/contents/<Packet.target_history>
```

Body:

```json
{
  "message": "PMP Vault GitHub Writer: add lossless inventory report history",
  "branch": "main",
  "content": "Base64Report"
}
```

No SHA is needed for a new history file.

### 9. Receipt

Show Notification:

```text
PMP Lossless Inventory Vault updated.
```

Optional: copy a compact receipt to clipboard:

```json
{
  "type": "PMP_VAULT_GITHUB_SHORTCUT_RECEIPT",
  "writer": "PMP Vault GitHub Writer",
  "current_report": "pmp-lossless-inventory-vault/current.json",
  "privacy_gate_passed": true
}
```

## App flow after Shortcut exists

Use:

```text
PMP app
→ Bridge
→ Improve Lossless Quality
→ Copy Lossless Report
```

The app will:

```text
create Vault Write Packet
copy it to clipboard
open shortcuts://run-shortcut?name=PMP%20Vault%20GitHub%20Writer
```

Then the Shortcut writes to GitHub.

## Fallback

If the Shortcut fails, upload/send the Vault Write Packet to ChatGPT. ChatGPT can use the GitHub connector as Vault GitHub Writer and update `current.json` manually.
