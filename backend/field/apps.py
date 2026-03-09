from django.apps import AppConfig
import os
import logging
logger = logging.getLogger(__name__)

class FieldConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'field'

    def ready(self):
        try:
            import ee
            # Attempt to initialize Earth Engine
            # This requires GOOGLE_APPLICATION_CREDENTIALS or gcloud auth
            try:
                project_id = os.environ.get('GEE_PROJECT')
                if not project_id:
                     logger.warning("GEE_PROJECT not set in .env, defaulting to 'nabard-field-data'")
                     project_id = "nabard-field-data"
                
                logger.info("Attempting to initialize Earth Engine with project: %s", project_id)
                ee.Initialize(project=project_id)
                logger.info("Earth Engine initialized successfully with project: %s", project_id)
            except ee.EEException as e:
                logger.error("Earth Engine initialization failed (EEException): %s", e)
                logger.error("Make sure you have run 'earthengine authenticate' and your GEE_PROJECT has Earthengine API enabled.")
                logger.warning("Earth Engine features will be disabled.")
            except Exception as e:
                logger.error("Earth Engine initialization failed (General): %s", e)
        except ImportError:
            logger.warning("earthengine-api not installed. Earth Engine features disabled.")
        except Exception as e:
            logger.error("Unexpected error in FieldConfig.ready: %s", e)