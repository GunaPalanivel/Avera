import os
import subprocess

import gradio as gr


def rank_candidates(file_obj):
    if file_obj is None:
        return "Please upload a JSONL file."

    input_path = file_obj.name
    output_path = "submission.csv"

    try:
        # Run the ranker pipeline
        result = subprocess.run(
            ["python", "rank.py", "--candidates", input_path, "--out", output_path],
            capture_output=True,
            text=True,
            check=True,
        )

        # Verify the output exists
        if not os.path.exists(output_path):
            return "Error: Output file was not generated."

        with open(output_path, encoding="utf-8") as f:
            content = f.read()

        return f"Successfully ranked candidates.\n\nExecution Log:\n{result.stdout}\n\nTop 100 Output:\n{content[:2000]}..."

    except subprocess.CalledProcessError as e:
        return f"Error executing ranking pipeline:\n{e.stderr}"


if __name__ == "__main__":
    demo = gr.Interface(
        fn=rank_candidates,
        inputs=gr.File(label="Upload candidates.jsonl", file_types=[".jsonl"]),
        outputs=gr.Textbox(label="Ranking Results & Logs", lines=25),
        title="Avera Ranking Engine Sandbox",
        description="Upload a JSONL file containing candidate profiles. The engine will parse, score, and rank the top 100 candidates deterministically.",
    )

    demo.launch(server_name="0.0.0.0", server_port=7860)
