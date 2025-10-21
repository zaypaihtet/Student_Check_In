// Auto-fetch public IP and show in alert (optional)
async function getIP() {
    try {
        const response = await fetch('https://api.ipify.org/?format=json');
        const data = await response.json();
        console.log("Student IP:", data.ip);
        return data.ip;
    } catch (err) {
        console.log("IP fetch error:", err);
        return "Unknown";
    }
}

getIP();
