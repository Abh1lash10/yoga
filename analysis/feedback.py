"""
Corrective Feedback Engine for AI Yoga Assistant.
Generates natural language, joint-specific corrective cues and provides
thread-safe, rate-limited voice announcements via pyttsx3.
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
from config import settings

logger = logging.getLogger(__name__)


class VoiceFeedbackWorker:
    """Thread-safe background speech synthesizer with cooldown and queueing."""

    def __init__(self):
        self.engine = None
        self._enabled = settings.VOICE_FEEDBACK_ENABLED
        self._last_spoken_time = 0.0
        self._last_spoken_text = ""
        self._lock = threading.Lock()
        self._init_tts()

    def _init_tts(self) -> None:
        """Attempts to initialize pyttsx3 offline TTS engine."""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", settings.VOICE_SPEECH_RATE)
            voices = self.engine.getProperty("voices")
            if voices:
                self.engine.setProperty("voice", voices[0].id)
            logger.info("pyttsx3 voice engine initialized successfully.")
        except Exception as e:
            logger.warning(f"Voice engine initialization disabled or failed: {e}")
            self.engine = None

    def speak(self, text: str, force: bool = False) -> None:
        """Speaks the text asynchronously if cooldown has elapsed."""
        if not self._enabled or not self.engine:
            return

        text = text.strip()
        if not text:
            return

        now = time.time()
        with self._lock:
            # Check cooldown and repeat text suppression
            if not force:
                if text == self._last_spoken_text and (now - self._last_spoken_time) < (settings.VOICE_COOLDOWN_SECONDS * 1.5):
                    return
                if (now - self._last_spoken_time) < settings.VOICE_COOLDOWN_SECONDS:
                    return

            self._last_spoken_time = now
            self._last_spoken_text = text

        def _run_speech():
            try:
                # Re-initialize or run on worker thread
                import pyttsx3
                local_engine = pyttsx3.init()
                local_engine.setProperty("rate", settings.VOICE_SPEECH_RATE)
                local_engine.say(text)
                local_engine.runAndWait()
            except Exception as ex:
                logger.debug(f"Speech output error: {ex}")

        threading.Thread(target=_run_speech, daemon=True).start()

    def set_enabled(self, enabled: bool) -> None:
        """Toggles voice feedback on or off."""
        self._enabled = enabled

    def is_enabled(self) -> bool:
        """Returns whether voice feedback is enabled."""
        return self._enabled and self.engine is not None


class FeedbackEngine:
    """Generates detailed, actionable joint-specific corrective cues."""

    def __init__(self):
        self.voice = VoiceFeedbackWorker()

    @staticmethod
    def format_joint_name(name: str) -> str:
        """Formats joint name from 'left_knee' to 'Left Knee'."""
        return name.replace("_", " ").title()

    @classmethod
    def generate_correction_message(
        cls,
        joint_name: str,
        actual_angle: float,
        target_angle: float,
        custom_rule_msg: Optional[str] = None
    ) -> str:
        """
        Generates specific, directional corrective instructions.
        
        Examples:
            - "Bend your left knee more (115° -> 90°)"
            - "Straighten your right elbow"
            - "Raise your left arm to shoulder level"
        """
        diff = actual_angle - target_angle
        abs_diff = abs(diff)
        joint_fmt = cls.format_joint_name(joint_name)

        if "knee" in joint_name:
            if target_angle > 150.0:
                return f"Straighten your {joint_fmt}"
            elif diff > 0:
                return f"Bend your {joint_fmt} deeper by about {int(abs_diff)}°"
            else:
                return f"Straighten your {joint_fmt} slightly by about {int(abs_diff)}°"

        elif "elbow" in joint_name:
            if target_angle > 150.0:
                return f"Straighten your {joint_fmt}"
            elif diff > 0:
                return f"Bend your {joint_fmt} more"
            else:
                return f"Extend your {joint_fmt} more"

        elif "shoulder" in joint_name:
            if diff < 0:
                return f"Raise your {joint_fmt} higher (target {int(target_angle)}°)"
            else:
                return f"Lower your {joint_fmt} slightly (target {int(target_angle)}°)"

        elif "hip" in joint_name:
            if diff < 0:
                return f"Open your {joint_fmt} more"
            else:
                return f"Hinge your {joint_fmt} deeper"

        elif "torso" in joint_name:
            if abs_diff > 10.0:
                return "Keep your torso centered and upright"

        # Fallback to custom rule message or generic
        if custom_rule_msg:
            return custom_rule_msg
        return f"Adjust your {joint_fmt}"

    def produce_primary_feedback(
        self,
        joint_results: List[Dict[str, Any]],
        overall_score: float,
        is_body_visible: bool = True,
        visibility_message: str = ""
    ) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        """
        Determines primary cue, text list, and structured cue objects with dot badges.
        
        Returns:
            Tuple of:
                - primary_message (str)
                - all_correction_messages (List[str])
                - structured_feedback (List[Dict[str, Any]])
        """
        if not is_body_visible:
            msg = visibility_message or "Please adjust position so your full body is visible."
            item = {"dot": "⚪", "color": "#94A3B8", "message": msg}
            return msg, [msg], [item]

        if overall_score >= settings.SCORE_EXCELLENT_THRESHOLD:
            msg = "Excellent posture! Hold steady."
            item = {"dot": "🟢", "color": "#10B981", "message": msg}
            return msg, [], [item]

        corrections: List[Tuple[float, str, Dict[str, Any]]] = []

        for res in joint_results:
            status_code = res.get("status_code", "CORRECT")
            if status_code != "CORRECT":
                deviation = abs(res.get("actual_angle", 0.0) - res.get("target_angle", 0.0))
                weight = res.get("weight", 10.0)
                priority = deviation * weight
                
                msg = res.get("feedback_message") or self.generate_correction_message(
                    res.get("joint_name", ""),
                    res.get("actual_angle", 0.0),
                    res.get("target_angle", 0.0)
                )

                dot = res.get("status_dot", "🔴")
                color = res.get("status_color", "#EF4444")
                cue_obj = {
                    "dot": dot,
                    "color": color,
                    "message": msg,
                    "joint_name": res.get("formatted_name", ""),
                }
                corrections.append((priority, msg, cue_obj))

        if not corrections:
            if overall_score >= settings.SCORE_GOOD_THRESHOLD:
                msg = "Good posture. Refine alignment slightly."
                return msg, [], [{"dot": "🟢", "color": "#10B981", "message": msg}]
            msg = "Adjust posture to match the reference pose."
            return msg, [], [{"dot": "🟡", "color": "#F59E0B", "message": msg}]

        # Sort by priority descending
        corrections.sort(key=lambda x: x[0], reverse=True)
        all_msgs = [c[1] for c in corrections]
        structured = [c[2] for c in corrections]
        primary_msg = all_msgs[0]

        return primary_msg, all_msgs, structured

    def speak_cue(self, text: str) -> None:
        """Dispatches text cue to TTS."""
        self.voice.speak(text)
