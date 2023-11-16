$(document).ready(function () {
    $('.alterar-status').on('click', function () {
        var idConta = $(this).data('id');
        var novoStatus = $(this).data('status');
        if (novoStatus = "activate") {
            $.ajax({
                url: `/activate_account/${idConta}`,
                type: 'POST',
                success: function (data) {
                    $('#contas-table').load(location.href + ' #contas-table');
                },
                error: function (error) {
                    console.error('Erro ao alterar o status da conta:', error);
                }
            });
        } else {
            $.ajax({
                url: `/deactivate_account/${idConta}`,
                type: 'POST',
                success: function (data) {
                    $('#contas-table').load(location.href + ' #contas-table');
                },
                error: function (error) {
                    console.error('Erro ao alterar o status da conta:', error);
                }
            });
        }
    });
});