export function getDirections(lat, lng) {
    // Check if the device is mobile
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    // Create the appropriate maps URL
    let mapsUrl;
    if (isMobile) {
        // Mobile devices - try to use native maps app
        if (navigator.platform.indexOf('iPhone') != -1 || 
            navigator.platform.indexOf('iPad') != -1 || 
            navigator.platform.indexOf('iPod') != -1) {
            mapsUrl = `maps://maps.apple.com/?daddr=${lat},${lng}`;
        } else {
            mapsUrl = `geo:${lat},${lng}?q=${lat},${lng}`;
        }
    } else {
        // Desktop - use Google Maps
        mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
    }
    
    // Open in new tab
    window.open(mapsUrl, '_blank');
}