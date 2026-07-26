import { ChangeEvent, FormEvent, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type ApiError = { message: string; details?: { line_number: number; message: string }[] };
type ValidationResponse = { line_count: number; warnings: string[] };
type Asset = { id: string; asset_type: string; content: string };
type Candidate = {
  candidate_id: string;
  start_seconds: number;
  end_seconds: number;
  transcript_excerpt: string;
  reason_selected: string;
  confidence: number;
  scores: Record<string, number | string> | null;
  assets: Asset[];
};

function App() {
  const [sourceTitle, setSourceTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "valid" | "error">("idle");
  const [message, setMessage] = useState("");
  const [warnings, setWarnings] = useState<string[]>([]);
  const [transcriptId, setTranscriptId] = useState("");
  const [segments, setSegments] = useState<{ id: string; start_seconds: number; end_seconds: number; text: string }[] | null>(null);
  const [candidateId, setCandidateId] = useState("");
  const [candidate, setCandidate] = useState<Candidate | null>(null);

  async function loadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) setRawText(await file.text());
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("loading");
    setWarnings([]);
    setSegments(null);
    const nextTranscriptId = crypto.randomUUID();
    try {
      const response = await fetch("http://127.0.0.1:8000/transcripts/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript_id: nextTranscriptId, source_content_id: crypto.randomUUID(), source_title: sourceTitle, raw_text: rawText }),
      });
      const body = (await response.json()) as ValidationResponse | ApiError;
      if (!response.ok) {
        const error = body as ApiError;
        setMessage([error.message, ...(error.details?.map((item) => `Line ${item.line_number}: ${item.message}`) ?? [])].join(" "));
        setStatus("error");
        return;
      }
      const result = body as ValidationResponse;
      setMessage(`Transcript validated: ${result.line_count} timestamped lines.`);
      setWarnings(result.warnings);
      setTranscriptId(nextTranscriptId);
      setStatus("valid");
    } catch {
      setMessage("Could not reach the ClipOps API. Start the backend and try again.");
      setStatus("error");
    }
  }

  async function loadSegments() {
    const response = await fetch(`http://127.0.0.1:8000/transcripts/${transcriptId}/segments`);
    if (!response.ok) return setMessage("Could not load transcript segments.");
    setSegments((await response.json()) as NonNullable<typeof segments>);
  }

  async function loadCandidate() {
    const response = await fetch(`http://127.0.0.1:8000/candidates/${candidateId}`);
    if (!response.ok) return setMessage("Candidate was not found.");
    setCandidate((await response.json()) as Candidate);
  }

  async function saveAsset(asset: Asset) {
    if (!candidate) return;
    await fetch(`http://127.0.0.1:8000/candidates/${candidate.candidate_id}/assets/${asset.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: asset.content }),
    });
  }

  return <main>
    <h1>ClipOps</h1><p>Start with a timestamped transcript.</p>
    <form onSubmit={submit}>
      <label>Source title<input value={sourceTitle} onChange={(event) => setSourceTitle(event.target.value)} required /></label>
      <label>Paste transcript<textarea value={rawText} onChange={(event) => setRawText(event.target.value)} required rows={14} /></label>
      <label>Or upload a .txt or .md transcript<input type="file" accept=".txt,.md,text/plain" onChange={loadFile} /></label>
      <button disabled={status === "loading"}>{status === "loading" ? "Validating…" : "Validate transcript"}</button>
    </form>
    {status !== "idle" && <p role={status === "error" ? "alert" : "status"}>{message}</p>}
    {warnings.map((warning) => <p className="warning" key={warning}>{warning}</p>)}
    <button disabled={status !== "valid"} onClick={loadSegments}>Review segments</button>
    {segments?.map((segment) => <article key={segment.id}><strong>{segment.start_seconds}s–{segment.end_seconds}s</strong><p>{segment.text}</p></article>)}
    <section><h2>Candidate detail</h2><label>Candidate ID<input value={candidateId} onChange={(event) => setCandidateId(event.target.value)} /></label><button onClick={loadCandidate}>Load candidate</button></section>
    {candidate && <section><h3>{candidate.start_seconds}s–{candidate.end_seconds}s</h3><p>{candidate.transcript_excerpt}</p><p>{candidate.reason_selected}</p><p>Confidence: {candidate.confidence}</p><pre>{JSON.stringify(candidate.scores, null, 2)}</pre>{candidate.assets.map((asset, index) => <label key={asset.id}>{asset.asset_type}<textarea value={asset.content} onChange={(event) => setCandidate({ ...candidate, assets: candidate.assets.map((item, itemIndex) => itemIndex === index ? { ...item, content: event.target.value } : item) })} /><button onClick={() => saveAsset(asset)}>Save</button></label>)}</section>}
  </main>;
}

createRoot(document.getElementById("root")!).render(<App />);
