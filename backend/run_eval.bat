@echo off
cd /d "%~dp0"
echo [%date% %time%] Starting LSTM evaluation... >> eval_progress.txt

.venv\Scripts\python.exe scripts/evaluate_lstm.py 1>eval_lstm_out.txt 2>eval_lstm_err.txt
echo [%date% %time%] LSTM exit code: %errorlevel% >> eval_progress.txt

echo [%date% %time%] Starting CNN training... >> eval_progress.txt
.venv\Scripts\python.exe scripts/train_cnn_multiclass.py --epochs 5 1>eval_cnn_out.txt 2>eval_cnn_err.txt
echo [%date% %time%] CNN exit code: %errorlevel% >> eval_progress.txt

echo [%date% %time%] Generating report... >> eval_progress.txt
.venv\Scripts\python.exe scripts/generate_report.py 1>eval_report_out.txt 2>eval_report_err.txt
echo [%date% %time%] Report exit code: %errorlevel% >> eval_progress.txt

echo [%date% %time%] ALL DONE >> eval_progress.txt
