import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd

class NRTL:
    """
    Implementación del modelo NRTL para sistemas binarios
    con parámetros ajustables según el artículo
    """
    def __init__(self, g12, g21, alpha12):
        """
        g12, g21: Parámetros de energía [J/mol] (equivalente a τ*RT en el artículo)
        alpha12: Parámetro de no-aleatoriedad
        """
        self.g12 = g12
        self.g21 = g21
        self.alpha12 = alpha12
        
    def gammas(self, x1, T):
        """
        Calcula coeficientes de actividad
        x1: Fracción molar del componente 1
        T: Temperatura en K
        """
        R = 8.314  # J/(mol·K)
        x2 = 1 - x1
        
        # Convertir a parámetros τ (adimensionales)
        tau12 = self.g12 / (R * T)
        tau21 = self.g21 / (R * T)
        
        # Prevenir errores numéricos
        alpha = max(0.01, min(self.alpha12, 0.5))
        
        # Cálculo de parámetros G
        G12 = np.exp(-alpha * tau12)
        G21 = np.exp(-alpha * tau21)
        
        # Coeficiente de actividad componente 1
        ln_gamma1 = x2**2 * (
            tau21 * (G21/(x1 + x2*G21))**2 + 
            (tau12 * G12)/(x2 + x1*G12)**2
        )
        
        # Coeficiente de actividad componente 2
        ln_gamma2 = x1**2 * (
            tau12 * (G12/(x2 + x1*G12))**2 + 
            (tau21 * G21)/(x1 + x2*G21)**2
        )
        
        return [np.exp(ln_gamma1), np.exp(ln_gamma2)]
    
    def excess_gibbs(self, x1, T):
        """
        Calcula la energía de Gibbs en exceso (J/mol)
        """
        gamma1, gamma2 = self.gammas(x1, T)
        return R * T * (x1 * np.log(gamma1) + (1 - x1) * np.log(gamma2))

# Constante de los gases
R = 8.314  # J/(mol·K)

# Función para ajuste de parámetros
def nrtl_model(x, g12, g21, alpha12):
    model = NRTL(g12, g21, alpha12)
    # Asumir temperatura promedio de 300K para ajuste
    return [model.gammas(xi, 300)[0] for xi in x]

# =============================================================================
# PROGRAMA PRINCIPAL - AJUSTE DE PARÁMETROS Y VISUALIZACIÓN
# =============================================================================
def main():
    # Datos de ejemplo basados en el artículo (Tabla 4: sistema PT)
    # x_Pe4NBr, gamma_Pe4NBr (Componente B)
    data_article = {
        'x_B': [0.1, 0.3, 0.5, 0.7, 0.9],
        'gamma_B': [2.8, 1.9, 1.3, 1.7, 2.5]  # Valores estimados de la Fig. 2
    }
    df = pd.DataFrame(data_article)
    x_data = df['x_B'].values
    gamma_data = df['gamma_B'].values

    # Configuración de parámetros iniciales
    print("="*60)
    print("MODELADO TERMODINÁMICO DE DES - MODELO NRTL")
    print("="*60)
    print("Ingrese los parámetros iniciales (valores recomendados del artículo):")
    
    # Valores recomendados del artículo (Tabla 4: sistema PT)
    g12_default = -2578.1  # J/mol (g12 para PT)
    g21_default = -9125.3   # J/mol (g21 para PT)
    alpha_default = 0.3
    
    try:
        g12 = float(input(f"Parámetro g12 [J/mol] (default={g12_default}): ") or g12_default)
        g21 = float(input(f"Parámetro g21 [J/mol] (default={g21_default}): ") or g21_default)
        alpha = float(input(f"Parámetro alpha (default={alpha_default}): ") or alpha_default)
    except ValueError:
        print("Error: Valores inválidos. Usando defaults.")
        g12, g21, alpha = g12_default, g21_default, alpha_default
    
    # Temperatura de referencia
    T_ref = float(input("Temperatura de referencia [K] (default=300): ") or 300)
    
    # Ajuste de parámetros
    print("\nAjustando parámetros...")
    try:
        params, _ = curve_fit(
            nrtl_model, 
            x_data, 
            gamma_data, 
            p0=[g12, g21, alpha],
            bounds=([-20000, -20000, 0.01], [0, 0, 0.5]),
            maxfev=5000
        )
        g12_opt, g21_opt, alpha_opt = params
        print("\n" + "="*50)
        print("RESULTADOS DEL AJUSTE")
        print("="*50)
        print(f"Parámetros optimizados:")
        print(f"g12 = {g12_opt:.2f} J/mol")
        print(f"g21 = {g21_opt:.2f} J/mol")
        print(f"alpha = {alpha_opt:.4f}")
    except Exception as e:
        print(f"Error en ajuste: {str(e)}")
        print("Usando parámetros iniciales para visualización")
        g12_opt, g21_opt, alpha_opt = g12, g21, alpha
    
    # Crear modelo con parámetros optimizados
    model = NRTL(g12_opt, g21_opt, alpha_opt)
    
    # =========================================================================
    # VISUALIZACIÓN DE RESULTADOS
    # =========================================================================
    plt.figure(figsize=(12, 9))
    
    # 1. Coeficientes de actividad
    x_test = np.linspace(0.01, 0.99, 100)
    gamma1_pred = [model.gammas(x, T_ref)[0] for x in x_test]
    gamma2_pred = [model.gammas(x, T_ref)[1] for x in x_test]
    
    ax1 = plt.subplot(221)
    ax1.scatter(x_data, gamma_data, c='red', s=80, label='Datos Experimentales (B)')
    ax1.plot(x_test, gamma1_pred, 'b-', lw=2, label='$\gamma_1$ (Modelo)')
    ax1.plot(x_test, gamma2_pred, 'g-', lw=2, label='$\gamma_2$ (Modelo)')
    ax1.set_title('Coeficientes de Actividad', fontsize=14)
    ax1.set_xlabel('Fracción Molar $x_B$', fontsize=12)
    ax1.set_ylabel('$\gamma$', fontsize=12)
    ax1.legend()
    ax1.grid(True)
    
    # 2. Energía de Gibbs en exceso
    G_E = [model.excess_gibbs(x, T_ref) for x in x_test]
    
    ax2 = plt.subplot(222)
    ax2.plot(x_test, G_E, 'm-', lw=2)
    ax2.set_title('Energía de Gibbs en Exceso', fontsize=14)
    ax2.set_xlabel('Fracción Molar $x_B$', fontsize=12)
    ax2.set_ylabel('$G^E$ (J/mol)', fontsize=12)
    ax2.grid(True)
    
    # 3. Diagrama comparativo con artículo (datos conceptuales)
    ax3 = plt.subplot(212)
    
    # Datos del artículo (Fig. 2 - Sistema PT)
    x_article = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    gammaB_article = np.array([2.5, 2.0, 1.6, 1.3, 1.1, 1.3, 1.6, 2.0, 2.5])
    gammaA_article = 1/(gammaB_article * x_article/(1-x_article))  # Estimado
    
    # Predicciones del modelo
    gammaB_model = [model.gammas(x, T_ref)[1] for x in x_article]
    
    ax3.scatter(x_article, gammaA_article, c='blue', s=80, label='$\gamma_A$ (Artículo)')
    ax3.scatter(x_article, gammaB_article, c='red', s=80, label='$\gamma_B$ (Artículo)')
    ax3.plot(x_article, gammaB_model, 'k--', lw=2, label='$\gamma_B$ (Modelo NRTL)')
    ax3.set_title('Comparación con Datos del Artículo (Sistema PT)', fontsize=14)
    ax3.set_xlabel('Fracción Molar $x_B$ (Pe$_4$NBr)', fontsize=12)
    ax3.set_ylabel('$\gamma$', fontsize=12)
    ax3.legend()
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig('nrtl_results_comparison.png', dpi=300)
    plt.show()
    
    # =========================================================================
    # EVALUACIÓN TERMODINÁMICA
    # =========================================================================
    print("\n" + "="*50)
    print("EVALUACIÓN TERMODINÁMICA")
    print("="*50)
    
    # Calcular punto eutéctico (mínimo en curva de líquidus)
    # Esto es una aproximación conceptual
    G_E_deriv = np.gradient(G_E, x_test[1]-x_test[0])
    eutectic_idx = np.argmin(G_E)
    x_eutectic = x_test[eutectic_idx]
    
    print(f"Fracción molar eutéctica estimada: {x_eutectic:.3f}")
    print(f"Energía de Gibbs en exceso mínima: {min(G_E):.2f} J/mol")
    
    # Interpretación de parámetros según artículo
    print("\nInterpretación de parámetros:")
    if g12_opt < 0 and g21_opt < 0:
        print("- Parámetros g12 y g21 negativos: Interacciones atractivas fuertes")
    if alpha_opt > 0.3:
        print("- Alpha > 0.3: Comportamiento no aleatorio significativo")

if __name__ == "__main__":
    main()