# covid19-ntnu

Active control code lies in the folders "System Identification" and "Control". MPC, Model Fitting and Simulink Models folders contain legacy code. Further cleanup of the codebase will happen soon.

The MATLAB code for numerical optimization depends on the open-source toolbox CasADi, which can be interfaced through MATLAB, but also OCTAVE and Python. See https://web.casadi.org/get/ for install instructions.

The network model (Python 2.7) interfaces the control code through the MATLAB engine API for python, see https://se.mathworks.com/help/matlab/matlab-engine-for-python.html
