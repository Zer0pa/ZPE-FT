<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

Navigation index for the ZPE-FT documentation surface.

This directory carries the audit path, runtime map, support routing, packet
contract, and integration notes for the current repo. The proof corpus lives in
`../proofs/` and is intentionally routed from here rather than duplicated.

---

<p>
  <img src="../.github/assets/readme/section-bars/faq-and-support.svg" alt="FAQ AND SUPPORT" width="100%">
</p>
<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Document</th>
      <th align="left">What it is</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>`docs/FAQ.md`</td>
      <td>Short first-contact answers about authority, release posture, helper expectations, and proof limits</td>
    </tr>
    <tr>
      <td>`docs/AUDITOR_PLAYBOOK.md`</td>
      <td>Shortest honest audit path for the current repo surface</td>
    </tr>
    <tr>
      <td>`docs/PUBLIC_AUDIT_LIMITS.md`</td>
      <td>Bounded-reading rules and explicit non-claims for public audits</td>
    </tr>
    <tr>
      <td>`docs/SUPPORT.md`</td>
      <td>Routing guide for bugs, evidence disputes, security reports, and licensing questions</td>
    </tr>
  </tbody>
</table>

---

<p>
  <img src="../.github/assets/readme/section-bars/interface-contracts.svg" alt="INTERFACE CONTRACTS" width="100%">
</p>
The authoritative technical contract surface for downstream readers lives here.

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Document</th>
      <th align="left">What it is</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>`docs/specs/ZPFIN_SPEC.md`</td>
      <td>Packet-format contract for the `.zpfin` surface and codec framing</td>
    </tr>
    <tr>
      <td>`docs/ARCHITECTURE.md`</td>
      <td>Canonical map of package, helper, script, proof, and release-truth surfaces</td>
    </tr>
    <tr>
      <td>`docs/INTEGRATION_PATTERN.md`</td>
      <td>Repo-local integration and observability pattern, including Comet and Opik tracking hooks</td>
    </tr>
    <tr>
      <td>`docs/examples/`</td>
      <td>Example request/config shapes for acquisition, corpus freeze, and benchmark inputs</td>
    </tr>
  </tbody>
</table>

---

<p>
  <img src="../.github/assets/readme/section-bars/runbooks.svg" alt="RUNBOOKS" width="100%">
</p>
Operator-local execution prompts and retained technical supplements live under
`../proofs/runbooks/`. They are preserved for lineage and execution context,
not promoted as the front-door public audit path.

---

<p>
  <img src="../.github/assets/readme/section-bars/proof-corpus.svg" alt="PROOF CORPUS" width="100%">
</p>
Read the current proof subset through these retained surfaces:

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Document</th>
      <th align="left">What it is</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>`../proofs/FINAL_STATUS.md`</td>
      <td>Current proof posture and governing blocker state</td>
    </tr>
    <tr>
      <td>`../proofs/CONSOLIDATED_PROOF_REPORT.md`</td>
      <td>Claim-by-claim evidence summary with bounded-reading notes</td>
    </tr>
    <tr>
      <td>`../proofs/HISTORICAL_PATH_LIMITS.md`</td>
      <td>What older reruns and path-bearing artifacts still mean, and what they no longer mean</td>
    </tr>
    <tr>
      <td>`../proofs/reruns/README.md`</td>
      <td>Routing guide for retained rerun directories and blocker packets</td>
    </tr>
  </tbody>
</table>

---

<p>
  <img src="../.github/assets/readme/section-bars/engineering-references.svg" alt="ENGINEERING REFERENCES" width="100%">
</p>
Use these stable in-repo references when you need canonical ownership or policy:

- `docs/DOC_REGISTRY.md`
- `docs/LEGAL_BOUNDARIES.md`
- `README.md`
- `RELEASING.md`
- `GOVERNANCE.md`

---

<p>
  <img src="../.github/assets/readme/section-bars/what-this-directory-is-not.svg" alt="WHAT THIS DIRECTORY IS NOT" width="100%">
</p>
This directory does not contain:

- release authority by itself; the root `README.md` and `../proofs/` still govern
- a license override for `LICENSE`
- a claim warehouse that upgrades bounded evidence into broader authority
- the external missing Phase 06 inputs that still block the open-access benchmark

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
