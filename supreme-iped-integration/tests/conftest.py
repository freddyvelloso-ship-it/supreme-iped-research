"""
Configuracao pytest para os testes de integração IPED.
"""
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: testes que requerem conexao com SUPREME backend (pular em CI sem stack)"
    )
