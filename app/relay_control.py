import os
from time import sleep
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WateringSystem:
    def __init__(self, gpio_pin=17):
        self.gpio_pin = gpio_pin
        self.is_watering = False
        self.last_watered = None
        self.mock_mode = os.getenv('MOCK_GPIO', 'false').lower() == 'true'
        
        if not self.mock_mode:
            try:
                from gpiozero import LED
                self.relay = LED(gpio_pin)
                logger.info(f"GPIO初期化成功: Pin {gpio_pin}")
            except Exception as e:
                logger.error(f"GPIO初期化エラー: {e}")
                logger.info("モックモードに切り替えます")
                self.mock_mode = True
        
        if self.mock_mode:
            logger.info("モックモードで動作中")
            self.relay = None
    
    def water_plants(self, duration=3):
        if self.is_watering:
            return False, "すでに水やり中です🌊"
        
        try:
            self.is_watering = True
            logger.info(f"水やり開始 ({duration}秒間)")
            
            if self.mock_mode:
                logger.info("[MOCK] リレーON")
            else:
                self.relay.on()
            
            sleep(duration)
            
            if self.mock_mode:
                logger.info("[MOCK] リレーOFF")
            else:
                self.relay.off()
            
            self.last_watered = datetime.datetime.now()
            self.is_watering = False
            
            logger.info("水やり完了")
            return True, "水やり完了しました！🌱"
            
        except Exception as e:
            logger.error(f"水やりエラー: {e}")
            self.is_watering = False
            return False, f"エラーが発生しました: {str(e)}"
    
    def get_status(self):
        return {
            "is_watering": self.is_watering,
            "last_watered": self.last_watered.isoformat() if self.last_watered else None,
            "last_watered_relative": self._get_relative_time() if self.last_watered else None,
            "mock_mode": self.mock_mode
        }
    
    def _get_relative_time(self):
        if not self.last_watered:
            return None
        
        delta = datetime.datetime.now() - self.last_watered
        
        if delta.seconds < 60:
            return "たった今"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"{minutes}分前"
        elif delta.seconds < 86400:
            hours = delta.seconds // 3600
            return f"{hours}時間前"
        else:
            days = delta.days
            return f"{days}日前"