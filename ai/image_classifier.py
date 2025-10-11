import os
import logging
from typing import Optional, Tuple, Dict
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class ImageIssueClassifier:
    """
    YOLO-based image issue detector using a local best.pt model only.
    Maps detected class names to civic issue categories heuristically.
    """
    
    SUPPORTED_ISSUES = [
        "garbage",
        "pothole", 
        "streetlight",
        "waterlogging",
        "encroachment",
    ]
    
    # Mapping of potential model outputs to our issue categories
    LABEL_MAPPINGS = {
        # Garbage/Waste related
        "trash": "garbage",
        "garbage": "garbage", 
        "waste": "garbage",
        "dump": "garbage",
        "litter": "garbage",
        "refuse": "garbage",
        "rubbish": "garbage",
        "debris": "garbage",
        "dumpster": "garbage",
        "landfill": "garbage",
        
        # Pothole/Road related
        "pothole": "pothole",
        "hole": "pothole",
        "asphalt": "pothole", 
        "road damage": "pothole",
        "crack": "pothole",
        "pavement": "pothole",
        "street": "pothole",
        "road": "pothole",
        "highway": "pothole",
        
        # Street light related
        "street light": "streetlight",
        "streetlight": "streetlight",
        "lamp": "streetlight", 
        "light pole": "streetlight",
        "lighting": "streetlight",
        "bulb": "streetlight",
        "illumination": "streetlight",
        
        # Water/flooding related
        "flood": "waterlogging",
        "water": "waterlogging",
        "waterlog": "waterlogging",
        "drainage": "waterlogging",
        "puddle": "waterlogging", 
        "overflow": "waterlogging",
        "stagnant": "waterlogging",
        
        # Encroachment related
        "encroach": "encroachment",
        "illegal structure": "encroachment",
        "kiosk": "encroachment",
        "unauthorized": "encroachment",
        "construction": "encroachment",
        "building": "encroachment",
        "structure": "encroachment",
    }
    
    def __init__(self, preview_output_dir: Optional[str] = None):
        """
        Args:
            preview_output_dir: Directory under static/ where annotated previews will be saved.
        """
        self.preview_output_dir = preview_output_dir or os.path.join(
            Path(__file__).resolve().parents[1], "static", "images", "detections"
        )
        os.makedirs(self.preview_output_dir, exist_ok=True)

        # YOLO model (required)
        self.yolo_model = None
        self.yolo_model_path = self._resolve_model_path()
        self._initialize_yolo()
    
    def _resolve_model_path(self) -> str:
        """Find best.pt in common in-project locations or via BEST_MODEL_PATH env."""
        # 1) Explicit env path
        env_path = os.getenv("BEST_MODEL_PATH")
        if env_path and os.path.exists(env_path):
            logger.info(f"Using BEST_MODEL_PATH from env: {env_path}")
            return env_path

        root = Path(__file__).resolve().parents[1]  # Segmentation-fault/
        candidates = [
            root / "best.pt",
            root / "ai" / "models" / "best.pt",
            root / "models" / "best.pt",
            root / "static" / "models" / "best.pt",
        ]
        
        logger.info(f"Searching for best.pt in project root: {root}")
        for p in candidates:
            logger.debug(f"Checking: {p} - Exists: {p.exists()}")
            if p.exists():
                logger.info(f"Found best.pt at: {p}")
                return str(p)
        
        # Default location under Segmentation-fault/best.pt
        default_path = str(root / "best.pt")
        logger.warning(f"best.pt not found in any candidate location. Defaulting to: {default_path}")
        return default_path

    def _initialize_yolo(self):
        """Initialize YOLO from local best.pt. No external services used."""
        try:
            if os.path.exists(self.yolo_model_path):
                from ultralytics import YOLO  # type: ignore
                self.yolo_model = YOLO(self.yolo_model_path)
                logger.info("Loaded YOLO model from %s", self.yolo_model_path)
            else:
                logger.error("best.pt not found at %s. Set BEST_MODEL_PATH or place file accordingly.", self.yolo_model_path)
        except Exception as e:
            logger.error("YOLO init failed: %s", e)
            self.yolo_model = None
    
    def _map_label_to_issue(self, raw_label: str) -> Optional[str]:
        """
        Map a raw classification label to our civic issue categories.
        
        Args:
            raw_label: Raw label from the model
            
        Returns:
            Mapped issue type or None if no mapping found
        """
        if not raw_label:
            return None
            
        # Convert to lowercase for comparison
        label_lower = raw_label.lower()
        
        # Direct mapping first
        if label_lower in self.LABEL_MAPPINGS:
            return self.LABEL_MAPPINGS[label_lower]
        
        # Check if any mapping key is contained in the label
        for keyword, issue_type in self.LABEL_MAPPINGS.items():
            if keyword in label_lower:
                return issue_type
        
        # Special cases with more complex logic
        if any(word in label_lower for word in ["broken", "damaged", "cracked"]):
            if any(word in label_lower for word in ["road", "street", "pavement"]):
                return "pothole"
            elif any(word in label_lower for word in ["light", "lamp", "bulb"]):
                return "streetlight"
        
        return None
    
    def classify_image(self, image_path: str) -> Optional[str]:
        """
        Classify a civic issue from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Classified issue type or None if classification fails
        """
        # Validate image path
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None
            
        # Use YOLO only
        if self.yolo_model is not None:
            info = self.classify_with_preview(image_path)
            return info.get("issue_type") if info else None
        
        logger.warning("YOLO model not available; cannot classify")
        return None

    def classify_with_preview(self, image_path: str) -> Optional[Dict[str, str]]:
        """
        Run detection/classification and produce an annotated preview image.

        Returns dict with keys: 'issue_type' and 'preview_path' (absolute path on disk).
        Uses YOLO if available; falls back to HF without preview if not.
        """
        if not os.path.exists(image_path):
            logger.error("Image file not found: %s", image_path)
            return None

        # YOLO path: detect and render
        if self.yolo_model is not None:
            try:
                results = self.yolo_model.predict(image_path, verbose=False)
                if not results:
                    return None
                res = results[0]

                # Determine issue type from top class (assumes class names map to our issues)
                cls_name = None
                if hasattr(res, 'probs') and getattr(res.probs, 'top1', None) is not None:
                    # For classification models
                    idx = int(res.probs.top1)
                    names = getattr(res, 'names', {}) or getattr(self.yolo_model, 'names', {})
                    cls_name = str(names.get(idx, "")) if isinstance(names, dict) else None
                elif len(getattr(res, 'boxes', [])) > 0:
                    # For detection models: use the class of the highest confidence box
                    try:
                        confs = res.boxes.conf.cpu().tolist()
                        best_i = confs.index(max(confs))
                        cls_idx = int(res.boxes.cls.cpu().tolist()[best_i])
                        names = getattr(res, 'names', {}) or getattr(self.yolo_model, 'names', {})
                        cls_name = str(names.get(cls_idx, "")) if isinstance(names, dict) else None
                    except Exception:
                        cls_name = None

                mapped_issue = self._map_label_to_issue((cls_name or "").lower()) if cls_name else None

                # Render annotated preview
                try:
                    import cv2  # type: ignore
                    import numpy as np  # type: ignore
                    plotted = res.plot()  # ndarray BGR
                    # File name
                    fname = f"det_{uuid.uuid4().hex[:8]}.jpg"
                    out_path = os.path.join(self.preview_output_dir, fname)
                    cv2.imwrite(out_path, plotted)
                except Exception as e:
                    logger.warning("Failed to save annotated preview: %s", e)
                    out_path = image_path  # fallback to original

                return {"issue_type": mapped_issue or cls_name or None, "preview_path": out_path}
            except Exception as e:
                logger.error("YOLO detection failed: %s", e)
                # Fall through to HF

        # No fallback: strictly local YOLO
        return None
    
    def get_supported_issues(self) -> list:
        """Get list of supported issue types."""
        return self.SUPPORTED_ISSUES.copy()
    
    def is_available(self) -> bool:
        """Check if the image classifier is available (YOLO)."""
        return self.yolo_model is not None
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_type": "ultralytics_yolo",
            "model_path": self.yolo_model_path,
            "available": self.is_available(),
            "supported_issues": self.get_supported_issues()
        }
