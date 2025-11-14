// API基础URL
const API_BASE_URL = window.location.origin + '/api';

// 表单提交处理
document.getElementById('tripForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // 获取表单数据
    const formData = getFormData();

    // 验证数据
    if (!validateFormData(formData)) {
        return;
    }

    // 显示加载状态
    showLoading(true);

    try {
        // 发送请求
        const response = await fetch(`${API_BASE_URL}/plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('请求失败');
        }

        const result = await response.json();

        if (result.success && result.data) {
            // 显示结果
            displayResults(result.data);
        } else {
            alert('行程规划失败：' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('错误:', error);
        alert('请求失败，请检查网络连接或稍后重试');
    } finally {
        showLoading(false);
    }
});

// 获取表单数据
function getFormData() {
    const city = document.getElementById('city').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const transportation = document.getElementById('transportation').value;
    const accommodation = document.getElementById('accommodation').value;
    const freeText = document.getElementById('freeText').value;

    // 获取选中的偏好
    const preferences = [];
    document.querySelectorAll('input[name="preferences"]:checked').forEach(checkbox => {
        preferences.push(checkbox.value);
    });

    // 计算旅行天数
    const start = new Date(startDate);
    const end = new Date(endDate);
    const travelDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;

    return {
        city,
        start_date: startDate,
        end_date: endDate,
        travel_days: travelDays,
        transportation,
        accommodation,
        preferences,
        free_text_input: freeText
    };
}

// 验证表单数据
function validateFormData(data) {
    if (!data.city) {
        alert('请输入目的地城市');
        return false;
    }

    if (!data.start_date || !data.end_date) {
        alert('请选择开始和结束日期');
        return false;
    }

    if (data.travel_days < 1) {
        alert('结束日期必须晚于或等于开始日期');
        return false;
    }

    if (data.travel_days > 30) {
        alert('旅行天数不能超过30天');
        return false;
    }

    return true;
}

// 显示加载状态
function showLoading(isLoading) {
    const btn = document.getElementById('planBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');

    if (isLoading) {
        btn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
    } else {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// 显示结果
function displayResults(data) {
    const resultSection = document.getElementById('resultSection');
    resultSection.style.display = 'block';

    // 显示概览
    displayOverview(data);

    // 显示预算
    displayBudget(data.budget);

    // 显示天气
    displayWeather(data.weather_info);

    // 显示每日行程
    displayDailyPlans(data.days);

    // 显示建议
    displaySuggestions(data.overall_suggestions);

    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// 显示概览
function displayOverview(data) {
    const content = document.getElementById('overviewContent');
    content.innerHTML = `
        <p><strong>目的地：</strong>${data.city}</p>
        <p><strong>旅行时间：</strong>${data.start_date} 至 ${data.end_date}</p>
        <p><strong>旅行天数：</strong>${data.days.length} 天</p>
        <p><strong>总景点数：</strong>${data.days.reduce((sum, day) => sum + day.attractions.length, 0)} 个</p>
    `;
}

// 显示预算
function displayBudget(budget) {
    if (!budget) return;

    const content = document.getElementById('budgetContent');
    content.innerHTML = `
        <table class="budget-table">
            <tr>
                <td class="label">景点门票</td>
                <td class="amount">¥${budget.total_attractions}</td>
            </tr>
            <tr>
                <td class="label">酒店住宿</td>
                <td class="amount">¥${budget.total_hotels}</td>
            </tr>
            <tr>
                <td class="label">餐饮费用</td>
                <td class="amount">¥${budget.total_meals}</td>
            </tr>
            <tr>
                <td class="label">交通费用</td>
                <td class="amount">¥${budget.total_transportation}</td>
            </tr>
            <tr style="border-top: 2px solid #667eea;">
                <td class="label total">总计</td>
                <td class="amount total">¥${budget.total}</td>
            </tr>
        </table>
    `;
}

// 显示天气
function displayWeather(weatherInfo) {
    const content = document.getElementById('weatherContent');

    if (!weatherInfo || weatherInfo.length === 0) {
        content.innerHTML = '<p>暂无天气信息</p>';
        return;
    }

    const weatherHTML = weatherInfo.map(weather => `
        <div class="weather-item">
            <div class="weather-date">${weather.date}</div>
            <div>${weather.day_weather}</div>
            <div class="weather-temp">${weather.day_temp}°C / ${weather.night_temp}°C</div>
            <div>${weather.wind_direction} ${weather.wind_power}</div>
        </div>
    `).join('');

    content.innerHTML = `<div class="weather-grid">${weatherHTML}</div>`;
}

// 显示每日行程
function displayDailyPlans(days) {
    const content = document.getElementById('dailyPlansContent');

    const daysHTML = days.map(day => `
        <div class="day-card">
            <div class="day-header">
                <div class="day-title">第 ${day.day_index + 1} 天 - ${day.date}</div>
                <div class="day-info">${day.transportation} | ${day.accommodation}</div>
            </div>
            
            <div class="day-description">
                <p><strong>${day.description}</strong></p>
            </div>
            
            ${day.hotel ? `
                <div class="hotel-info">
                    <div class="hotel-name">🏨 ${day.hotel.name}</div>
                    <p>📍 ${day.hotel.address}</p>
                    <p>💰 ${day.hotel.price_range} | ⭐ ${day.hotel.rating}</p>
                </div>
            ` : ''}
            
            <div class="attractions-section">
                <h4>景点安排</h4>
                <div class="attractions-list">
                    ${day.attractions.map(attraction => `
                        <div class="attraction-item">
                            ${attraction.image_url ?
            `<img src="${attraction.image_url}" alt="${attraction.name}" class="attraction-image">` :
            `<div class="attraction-image-placeholder">🏛️</div>`
        }
                            <div class="attraction-details">
                                <div class="attraction-name">${attraction.name}</div>
                                <div class="attraction-address">📍 ${attraction.address}</div>
                                <div class="attraction-info">
                                    ⏱️ 建议游览 ${attraction.visit_duration} 分钟 | 
                                    🎫 门票 ¥${attraction.ticket_price}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="meals-section">
                <h4>餐饮安排</h4>
                <div class="meals-list">
                    ${day.meals.map(meal => `
                        <div class="meal-item">
                            <div class="meal-type">
                                ${meal.type === 'breakfast' ? '🌅 早餐' :
                meal.type === 'lunch' ? '🌞 午餐' : '🌙 晚餐'}
                            </div>
                            <div class="meal-name">${meal.name}</div>
                            ${meal.description ? `<div class="meal-desc">${meal.description}</div>` : ''}
                            <div class="meal-cost">约 ¥${meal.estimated_cost}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `).join('');

    content.innerHTML = daysHTML;
}

// 显示建议
function displaySuggestions(suggestions) {
    const content = document.getElementById('suggestionsContent');

    // 将换行符转换为HTML换行
    const suggestionsHTML = suggestions.split('\n').map(line =>
        line.trim() ? `<p>${line}</p>` : ''
    ).join('');

    content.innerHTML = `<div class="suggestions-content">${suggestionsHTML}</div>`;
}

// 设置最小日期为今天
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').min = today;
    document.getElementById('endDate').min = today;

    // 当开始日期改变时，更新结束日期的最小值
    document.getElementById('startDate').addEventListener('change', (e) => {
        document.getElementById('endDate').min = e.target.value;
    });
});
