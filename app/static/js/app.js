class WateringApp {
    constructor() {
        this.waterButton = document.getElementById('waterButton');
        this.tomato = document.getElementById('tomato');
        this.lastWateredEl = document.getElementById('lastWatered');
        this.todayCountEl = document.getElementById('todayCount');
        this.messageEl = document.getElementById('message');
        this.statusTextEl = document.getElementById('statusText');
        this.durationSlider = document.getElementById('duration');
        this.durationValue = document.getElementById('durationValue');
        
        this.todayCount = 0;
        this.lastWateredDate = null;
        
        this.init();
    }
    
    init() {
        this.waterButton.addEventListener('click', () => this.waterPlants());
        this.durationSlider.addEventListener('input', (e) => {
            this.durationValue.textContent = e.target.value;
        });
        this.updateStatus();
        setInterval(() => this.updateRelativeTime(), 60000);
    }
    
    async waterPlants() {
        if (this.waterButton.disabled) return;
        
        const duration = parseInt(this.durationSlider.value);
        
        this.waterButton.disabled = true;
        this.waterButton.classList.add('watering');
        this.waterButton.querySelector('.button-text').textContent = '水やり中...';
        this.showMessage(`お水をあげています... ${duration}秒間 💧`, 'info');
        this.statusTextEl.textContent = 'お水をもらって喜んでいます！';
        
        try {
            const response = await fetch('/api/water', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ duration: duration })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.onWateringSuccess(data);
            } else {
                this.onWateringError(data.message);
            }
        } catch (error) {
            this.onWateringError('接続エラーが発生しました');
        }
    }
    
    onWateringSuccess(data) {
        this.waterButton.classList.remove('watering');
        this.tomato.classList.add('happy');
        this.showMessage('水やり完了しました！ 🎉', 'success');
        this.statusTextEl.textContent = 'ありがとう！元気いっぱい！';
        
        this.todayCount++;
        this.todayCountEl.textContent = `${this.todayCount}回`;
        this.lastWateredDate = new Date();
        this.updateRelativeTime();
        
        this.showRainbowEffect();
        
        setTimeout(() => {
            this.tomato.classList.remove('happy');
            this.waterButton.disabled = false;
            this.waterButton.querySelector('.button-text').textContent = 'お水をあげる';
            this.clearMessage();
            this.statusTextEl.textContent = '元気いっぱい！';
        }, 3000);
    }
    
    onWateringError(message) {
        this.waterButton.classList.remove('watering');
        this.waterButton.disabled = false;
        this.waterButton.querySelector('.button-text').textContent = 'お水をあげる';
        this.showMessage(message || 'エラーが発生しました', 'error');
        this.statusTextEl.textContent = '元気いっぱい！';
        
        setTimeout(() => this.clearMessage(), 3000);
    }
    
    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.last_watered_relative) {
                this.lastWateredEl.textContent = data.last_watered_relative;
            }
            
            if (data.last_watered) {
                this.checkAndResetDailyCount(new Date(data.last_watered));
            }
        } catch (error) {
            console.error('ステータス取得エラー:', error);
        }
    }
    
    updateRelativeTime() {
        if (!this.lastWateredDate) return;
        
        const now = new Date();
        const diff = now - this.lastWateredDate;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        
        if (minutes < 1) {
            this.lastWateredEl.textContent = 'たった今';
        } else if (minutes < 60) {
            this.lastWateredEl.textContent = `${minutes}分前`;
        } else if (hours < 24) {
            this.lastWateredEl.textContent = `${hours}時間前`;
        } else {
            const days = Math.floor(hours / 24);
            this.lastWateredEl.textContent = `${days}日前`;
        }
    }
    
    checkAndResetDailyCount(lastWateredDate) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        lastWateredDate.setHours(0, 0, 0, 0);
        
        if (lastWateredDate.getTime() !== today.getTime()) {
            this.todayCount = 0;
            this.todayCountEl.textContent = '0回';
        }
    }
    
    showMessage(text, type) {
        this.messageEl.textContent = text;
        this.messageEl.className = `message ${type}`;
    }
    
    clearMessage() {
        this.messageEl.textContent = '';
        this.messageEl.className = 'message';
    }
    
    showRainbowEffect() {
        const rainbow = document.createElement('div');
        rainbow.className = 'rainbow';
        rainbow.textContent = '🌈';
        document.body.appendChild(rainbow);
        
        setTimeout(() => rainbow.remove(), 2000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new WateringApp();
});