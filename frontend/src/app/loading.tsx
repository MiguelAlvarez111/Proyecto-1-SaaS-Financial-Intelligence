/**
 * Shown while the page segment is loading.
 * If you see this forever, the page component is not finishing (build/compile issue).
 */
export default function Loading() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)",
        color: "#94a3b8",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <p>Loading…</p>
    </div>
  );
}
