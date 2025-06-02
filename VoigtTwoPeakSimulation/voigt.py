import numpy as np
from scipy.special import wofz

def voigt(x, center, intensity, gamma_L, gamma_G):
    """
    Voigt线型函数
    参数：
    x: 波数数组
    center: 中心位置 (cm-1)
    intensity: 峰强度
    gamma_L: 洛伦兹半高宽
    gamma_G: 高斯半高宽 
    """
    sigma = gamma_G / np.sqrt(2 * np.log(2))
    z = ((x - center) + 1j * gamma_L) / (sigma * np.sqrt(2))
    return intensity * np.real(wofz(z)) / (sigma * np.sqrt(2 * np.pi))
