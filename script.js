// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    // Seleciona todos os botões que fazem parte do agendamento
    const scheduleButtons = document.querySelectorAll('.schedule-button');

    scheduleButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Verifica se o botão é branco (disponível para ser agendado pelo usuário)
            // Ou seja, NÃO possui as classes 'booked' (vermelho), 'available' (verde inicial da imagem)
            // nem 'selected-by-user' (verde agendado pelo próprio usuário)
            const isWhite = !button.classList.contains('booked') &&
                            !button.classList.contains('available') &&
                            !button.classList.contains('selected-by-user');

            if (isWhite) {
                // Se for branco, muda para verde para sinalizar que foi "agendado por você"
                button.classList.add('selected-by-user');

                // --- INTEGRATION WITH BACKEND (CONCEPTUAL) ---
                // Se você quiser que este agendamento seja persistente
                // (visível para outros usuários ou após um refresh da página),
                // você ainda precisará de um backend (como o Flask) para armazenar isso.
                //
                // Exemplo (pseudocódigo para enviar ao backend Python):
                // const scheduleId = button.id; // Ex: "btn-segunda-0700"
                // fetch('/api/book_schedule', { // Esta rota precisa ser implementada no seu app.py
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json',
                //     },
                //     body: JSON.stringify({ schedule_id: scheduleId, action: 'book' })
                // })
                // .then(response => response.json())
                // .then(data => {
                //     if (data.success) {
                //         console.log('Horário agendado com sucesso no backend!', data);
                //         // Opcional: Você pode querer que o backend retorne o status final
                //         // e você atualize o botão com base nessa resposta para maior robustez.
                //     } else {
                //         console.error('Erro ao agendar horário no backend:', data.message);
                //         // Se falhar no backend, reverte a cor no frontend
                //         button.classList.remove('selected-by-user');
                //         alert('Erro ao agendar: ' + data.message);
                //     }
                // })
                // .catch(error => {
                //     console.error('Erro de rede ao agendar horário:', error);
                //     button.classList.remove('selected-by-user'); // Reverte em caso de erro de rede
                //     alert('Erro de conexão. Tente novamente.');
                // });
                // --------------------------------------------------

            } else {
                // Se for vermelho (ocupado), verde (já marcado ou agendado por você), não faz nada
                console.log('Este horário não está disponível para agendamento.');
            }
        });
    });
});