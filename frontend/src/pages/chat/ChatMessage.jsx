// import ReactMarkdown from "react-markdown"
// import remarkGfm from "remark-gfm"

// function sanitizeMarkdown(md) {
//   const fences = (md.match(/```/g) || []).length
//   if (fences % 2 !== 0) {
//     return md + "\n```"
//   }
//   return md
// }

// export default function ChatMessage({ role, content, streaming }) {
//   const isUser = role === "user"
//   // Show shimmer when assistant is streaming but no content has arrived yet
//   const isPending = !isUser && streaming && !content

//   return (
//     <div className={`chat-message-wrapper ${isUser ? "user-wrapper" : "assistant-wrapper"}`}>
//       <div className={`chat-message ${isUser ? "user" : "assistant"} ${isPending ? "assistant--shimmer" : ""}`}>
//         {isPending ? (
//           <div className="shimmer-lines">
//             <div className="shimmer-line shimmer-line--long" />
//             <div className="shimmer-line shimmer-line--medium" />
//             <div className="shimmer-line shimmer-line--short" />
//           </div>
//         ) : (
//           <>
//             <ReactMarkdown remarkPlugins={[remarkGfm]}>
//               {sanitizeMarkdown(content)}
//             </ReactMarkdown>
//             {streaming && <span className="streaming-cursor">▍</span>}
//           </>
//         )}
//       </div>
//     </div>
//   )
// }

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

function sanitizeMarkdown(md) {
  const fences = (md.match(/```/g) || []).length
  if (fences % 2 !== 0) return md + "\n```"
  return md
}

export default function ChatMessage({ role, content, status, streaming }) {
  const isUser = role === "user"
  const isPending = !isUser && streaming && !content && !status

  return (
    <div className={`chat-message-wrapper ${isUser ? "user-wrapper" : "assistant-wrapper"}`}>
      <div className={`chat-message ${isUser ? "user" : "assistant"} ${isPending ? "assistant--shimmer" : ""}`}>
        {isPending ? (
          <div className="shimmer-lines">
            <div className="shimmer-line shimmer-line--long" />
            <div className="shimmer-line shimmer-line--medium" />
            <div className="shimmer-line shimmer-line--short" />
          </div>
        ) : (
          <>
            {status && (
              <div className="tool-status">
                {status.split("\n").filter(Boolean).map((line, i) => (
                  <div key={i} className="tool-status-line">{line}</div>
                ))}
              </div>
            )}
            {content && (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {sanitizeMarkdown(content)}
              </ReactMarkdown>
            )}
            {streaming && <span className="streaming-cursor">▍</span>}
          </>
        )}
      </div>
    </div>
  )
}