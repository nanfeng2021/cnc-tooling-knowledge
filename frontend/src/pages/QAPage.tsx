import { useState } from "react";
import { useQAStore } from "@/stores/qaStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const EXAMPLE_QUESTIONS = [
  "What end mill is good for steel?",
  "Carbide drill for aluminum",
  "Best milling cutter for stainless steel?",
  "Turning tool for cast iron",
];

export default function QAPage() {
  const [question, setQuestion] = useState("");
  const { result, loading, error, askQuestion, reset } = useQAStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) askQuestion(question.trim());
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">智能问答</h1>
        <p className="text-muted-foreground">输入关于刀具的自然语言问题，获取知识库中的专业回答</p>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          placeholder="例如：加工钢材用什么立铣刀？"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="flex-1"
        />
        <Button type="submit" disabled={loading || !question.trim()}>
          {loading ? "搜索中..." : "提问"}
        </Button>
      </form>

      <div className="flex flex-wrap gap-2">
        {EXAMPLE_QUESTIONS.map((q) => (
          <Button
            key={q}
            variant="outline"
            size="sm"
            onClick={() => {
              setQuestion(q);
              askQuestion(q);
            }}
          >
            {q}
          </Button>
        ))}
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6 text-destructive">{error}</CardContent>
        </Card>
      )}

      {result && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                回答
                <Badge variant={result.confidence > 0.5 ? "default" : "secondary"}>
                  置信度 {(result.confidence * 100).toFixed(0)}%
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap text-sm font-sans">{result.answer}</pre>
            </CardContent>
          </Card>

          {result.sources.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>参考来源 ({result.sources.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.sources.map((src) => (
                    <div key={src.cutter_id} className="flex items-center justify-between rounded border p-3">
                      <div>
                        <p className="font-medium">{src.cutter_name}</p>
                        <p className="text-xs text-muted-foreground">{src.summary}</p>
                      </div>
                      <Badge variant="outline">{(src.relevance_score * 100).toFixed(0)}%</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Button variant="outline" onClick={reset}>
            清除结果
          </Button>
        </div>
      )}
    </div>
  );
}
