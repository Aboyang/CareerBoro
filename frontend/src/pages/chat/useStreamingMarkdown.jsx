import { useEffect, useRef, useState } from "react"

export function useStreamingMarkdown() {
  const bufferRef = useRef("")
  const [display, setDisplay] = useState("")

  function append(chunk) {
    bufferRef.current = chunk
  }

  useEffect(() => {
    const interval = setInterval(() => {
      setDisplay(bufferRef.current)
    }, 50) // 20fps

    return () => clearInterval(interval)
  }, [])

  return { display, append }
}
