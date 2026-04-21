from ui.pdf_export import generate_pdf_report

# ===== 模拟 analyzer 输出 =====
analysis = {
    "sigma": 6.23,
    "mid": 0.0075,
    "effective_rank": 3.12,
    "ssi": 0.42,
    "risk_score": 0.135,
    "eigvals": [3.2, 1.5, 0.7, 0.2, 0.05, 0.01],
}

# ===== 生成 PDF =====
filename, pdf_bytes = generate_pdf_report(analysis)

# ===== 写入文件 =====
with open(filename, "wb") as f:
    f.write(pdf_bytes)

print("PDF generated:", filename)
