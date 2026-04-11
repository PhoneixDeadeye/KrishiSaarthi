@echo off
setlocal
cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
set LOG=eval_pipeline_log.txt
set DS_PATH=datasets\New Plant Diseases Dataset(Augmented)\New Plant Diseases Dataset(Augmented)\train

echo [%date% %time%] === FULL PIPELINE START === > %LOG%

:: Step 1: LSTM Training on real ERA5 data
echo [%date% %time%] LSTM training starting... >> %LOG%
%PYTHON% scripts/train_lstm_risk.py --epochs 30 1>eval_lstm_train_out.txt 2>eval_lstm_train_err.txt
echo [%date% %time%] LSTM training exit: %errorlevel% >> %LOG%

:: Step 2: CNN Training on PlantVillage (dataset already downloaded)
echo [%date% %time%] CNN training starting... >> %LOG%
%PYTHON% scripts/train_cnn_multiclass.py --epochs 10 --dataset-path "%DS_PATH%" 1>eval_cnn_out.txt 2>eval_cnn_err.txt
echo [%date% %time%] CNN training exit: %errorlevel% >> %LOG%

:: Step 3: LSTM Evaluation on real test set
echo [%date% %time%] LSTM evaluation starting... >> %LOG%
%PYTHON% scripts/evaluate_lstm.py 1>eval_lstm_out.txt 2>eval_lstm_err.txt
echo [%date% %time%] LSTM eval exit: %errorlevel% >> %LOG%

:: Step 4-6: Validations (health score, carbon credits, yield)
echo [%date% %time%] Validations starting... >> %LOG%
%PYTHON% scripts/validate_health_score.py 1>eval_health_out.txt 2>eval_health_err.txt
echo [%date% %time%] Health score exit: %errorlevel% >> %LOG%
%PYTHON% scripts/validate_carbon_credits.py 1>eval_cc_out.txt 2>eval_cc_err.txt
echo [%date% %time%] Carbon credit exit: %errorlevel% >> %LOG%
%PYTHON% scripts/validate_yield.py 1>eval_yield_out.txt 2>eval_yield_err.txt
echo [%date% %time%] Yield exit: %errorlevel% >> %LOG%

:: Step 7: Generate report
echo [%date% %time%] Report generation starting... >> %LOG%
%PYTHON% scripts/generate_report.py 1>eval_report_out.txt 2>eval_report_err.txt
echo [%date% %time%] Report exit: %errorlevel% >> %LOG%

echo [%date% %time%] === PIPELINE COMPLETE === >> %LOG%
