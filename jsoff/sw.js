self.addEventListener('fetch', (event) => {
  // Minimalna obsługa zdarzenia fetch wymagana przez przeglądarki
  event.respondWith(fetch(event.request));
});
