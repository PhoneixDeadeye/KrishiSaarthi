"""
Enhanced health check endpoint with detailed component status
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KrishiSaarthi.settings')
import django
django.setup()

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time


def health_check(request):
    """
    Comprehensive health check endpoint
    Returns 200 if all critical components are healthy
    Returns 503 if any critical component is down
    """
    start_time = time.time()
    checks = {
        'status': 'healthy',
        'timestamp': time.time(),
        'components': {}
    }
    
    all_healthy = True
    
    # 1. Database Check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks['components']['database'] = {
            'status': 'healthy',
            'message': 'Database connection OK'
        }
    except Exception as e:
        checks['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        if cache_value == 'ok':
            checks['components']['cache'] = {
                'status': 'healthy',
                'message': 'Redis cache OK'
            }
        else:
            raise Exception('Cache read/write failed')
    except Exception as e:
        checks['components']['cache'] = {
            'status': 'degraded',
            'warning': str(e),
            'message': 'Application can run without cache'
        }
        # Cache is not critical, don't fail health check
    
    # 3. ML Models Check
    ml_models_path = Path(settings.BASE_DIR) / 'ml_models'
    required_models = [
        'crop_health_model.pth',
        'risk_lstm_final.pth',
        'risk_scaler.save'
    ]
    
    missing_models = []
    for model in required_models:
        if not (ml_models_path / model).exists():
            missing_models.append(model)
    
    if missing_models:
        checks['components']['ml_models'] = {
            'status': 'degraded',
            'missing': missing_models,
            'message': 'Some ML features may be unavailable'
        }
    else:
        checks['components']['ml_models'] = {
            'status': 'healthy',
            'message': 'All ML models present'
        }
    
    # 4. Disk Space Check
    try:
        import shutil
        total, used, free = shutil.disk_usage(settings.BASE_DIR)
        free_percent = (free / total) * 100
        
        if free_percent < 10:
            checks['components']['disk_space'] = {
                'status': 'critical',
                'free_percent': round(free_percent, 2),
                'message': 'Low disk space'
            }
            all_healthy = False
        elif free_percent < 20:
            checks['components']['disk_space'] = {
                'status': 'warning',
                'free_percent': round(free_percent, 2)
            }
        else:
            checks['components']['disk_space'] = {
                'status': 'healthy',
                'free_percent': round(free_percent, 2)
            }
    except Exception as e:
        checks['components']['disk_space'] = {
            'status': 'unknown',
            'error': str(e)
        }
    
    # 5. Memory Check
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent > 90:
            checks['components']['memory'] = {
                'status': 'critical',
                'usage_percent': memory_percent
            }
            all_healthy = False
        elif memory_percent > 80:
            checks['components']['memory'] = {
                'status': 'warning',
                'usage_percent': memory_percent
            }
        else:
            checks['components']['memory'] = {
                'status': 'healthy',
                'usage_percent': memory_percent
            }
    except ImportError:
        checks['components']['memory'] = {
            'status': 'unknown',
            'message': 'psutil not installed'
        }
    
    # Overall status
    checks['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
    
    if not all_healthy:
        checks['status'] = 'unhealthy'
        return JsonResponse(checks, status=503)
    
    return JsonResponse(checks, status=200)


def ready_check(request):
    """
    Readiness check - is the application ready to serve traffic?
    Stricter than health check
    """
    checks = {
        'ready': True,
        'checks': {}
    }
    
    # Database must be ready
    try:
        from django.contrib.auth.models import User
        User.objects.count()
        checks['checks']['database'] = True
    except Exception:
        checks['ready'] = False
        checks['checks']['database'] = False
    
    # Tables must exist
    try:
        from field.models import FieldData
        FieldData.objects.count()
        checks['checks']['migrations'] = True
    except Exception:
        checks['ready'] = False
        checks['checks']['migrations'] = False
    
    status_code = 200 if checks['ready'] else 503
    return JsonResponse(checks, status=status_code)


def liveness_check(request):
    """
    Liveness check - is the process alive?
    Simple check that returns 200 if the process is running
    """
    return JsonResponse({
        'alive': True,
        'timestamp': time.time()
    })
    else:
        print(f"{RED}{BOLD}✗ {passed}/{total} checks passed. System not ready.{RESET}")
        print(f"\n{YELLOW}Please fix the issues above before running the server.{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
