models_composelector = [
    # DIGIMAT MF
    {
        'workflowgenerator_classname': 'DigimatApplication',
        'workflowgenerator_module': '',

        'Name': 'Digimat-MF AIRBUS',
        'ID': 'Digimat-MF-a',
        'Description': 'Mean Field Homogenization for Airbus case',
        'Physics': {
            'Type': 'Continuum'
        },
        'Solver': {
            'Software': 'Digimat-MF-2018.1',
            'Language': 'C++',
            'License': 'Commercial',
            'Creator': 'e-Xstream',
            'Version_date': '05/2019',
            'Type': 'mean-field homogenization',
            'Documentation': 'https://www.e-xstream.com/products/tools/digimat-mf',
            'Estim_time_step_s': 1,
            'Estim_comp_time_s': 0.01,
            'Estim_execution_cost_EUR': 0.01,
            'Estim_personnel_cost_EUR': 0.01,
            'Required_expertise': 'None',
            'Accuracy': 'Medium',
            'Sensitivity': 'Low',
            'Complexity': 'Low',
            'Robustness': 'Very high'
        },

        'Inputs': [
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_MatrixYoung', 'Name': 'Young modulus of the matrix', 'Description': 'Young modulus of the matrix', 'Units': 'MPa', 'Origin': 'Database', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_InclusionYoung', 'Name': 'Young modulus of the inclusion', 'Description': 'Young modulus of the inclusion', 'Units': 'MPa', 'Origin': 'Database', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_MatrixPoisson', 'Name': 'Poisson\'s ration of the matrix', 'Description': 'Poisson\'s ration of the matrix', 'Units': 'None', 'Origin': 'Database', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_InclusionPoisson', 'Name': 'Poisson\'s ration of the inclusion', 'Description': 'Poisson\'s ration of the inclusion', 'Units': 'None', 'Origin': 'Database', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_InclusionVolumeFraction', 'Name': 'Volume Fraction of the Inclusion', 'Description': 'Volume Fraction of the Inclusion', 'Units': 'None', 'Origin': 'Database', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_InclusionAspectRatio', 'Name': 'Aspect Ratio of the Inclusion', 'Description': 'Aspect Ratio of the Inclusion', 'Units': 'None', 'Origin': 'Database', 'Required': True}
        ],
        'Outputs': [
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CompositeAxialYoung', 'Name': 'E_axial', 'Description': 'Axial Young modulus of the composite', 'Units': 'MPa'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CompositeInPlaneYoung', 'Name': 'E_plane', 'Description': 'Young modulus in the plane of the composite', 'Units': 'MPa'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CompositeInPlaneShear', 'Name': 'G_plane', 'Description': 'Shear modulus in the plane of the composite', 'Units': 'MPa'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CompositeTransverseShear', 'Name': 'G_transverse', 'Description': 'Transverse shear modulus of the composite', 'Units': 'MPa'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CompositeInPlanePoisson', 'Name': 'nu_plane', 'Description': 'Poisson\'s ration in the plane of the composite', 'Units': 'None'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CompositeTransversePoisson', 'Name': 'nu_transverse', 'Description': 'Transverse Poisson\'s ration of the composite', 'Units': 'None'},
        ]
    },

    # DIGIMAT FE
    {
        'workflowgenerator_classname': 'DigimatApplicationGYRFE',
        'workflowgenerator_module': '',

        'Name': 'Digimat-FE GOODYEAR',
        'ID': 'Digimat-FE-g',
        'Description': 'Full Field Homogenization for GoodYear case (SBR with Silica)',
        'Solver': {
            'Software': 'Digimat-FE-2018.1',
            'Language': 'C++',
            'License': 'Commercial',
            'Creator': 'Vincent',
            'Version_date': '05/2019',
            'Type': 'Full Field Homogenization',
            'Documentation': 'Where is it documented',
            'Estim_time_step_s': 1,
            'Estim_comp_time_s': 10000,
            'Estim_execution_cost_EUR': 0.01,
            'Estim_personnel_cost_EUR': 0.01,
            'Required_expertise': 'None',
            'Accuracy': 'High',
            'Sensitivity': 'High',
            'Complexity': 'Low',
            'Robustness': 'High'
        },
        'Physics': {
            'Type': 'Continuum',
            'Entity': 'Other'
        },
        'Inputs': [
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_Time_step', 'Name': 'Time step', 'Description': 'Time step', 'Units': 's', 'Origin': 'Simulated', 'Required': True}
        ],
        'Outputs': [
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_Time', 'Name': 'Cummulative time', 'Description': 'Cummulative time', 'Units': 's', 'Origin': 'Simulated'}
        ]
    },


    # MUL2
    {
        'workflowgenerator_classname': 'mul2code',
        'workflowgenerator_module': '',

        'Name': 'MUL2',
        'ID': 'MUL2-ID-1',
        'Description': 'MUL2-FEM code for structural analysis',
        'Physics': {
            'Type': 'Continuum',
            'Entity': 'Finite volume',
            'Equation': ['Linearized buckling'],
            'Equation_quantities': ['Stiffness matrix', 'Buckling load', 'Geometric stress matrix', 'Buckling mode vector'],
            'Relation_description': ['Linear elastic'],
            'Relation_formulation': ['Carrera Unified Formulation (CUF)'],
            'Representation': 'Finite volumes'
        },
        'Solver': {
            'Software': 'MUL2 FEM',
            'Language': 'Fortran',
            'License': 'LGPL',
            'Creator': 'MUL2 Group - IK',
            'Version_date': '1.0 May 2019',
            'Type': 'Finite elements',
            'Documentation': 'NA',
            'Estim_time_step_s': 10,
            'Estim_comp_time_s': 0.1,
            'Estim_execution_cost_EUR': 0.1,
            'Estim_personnel_cost_EUR': 0.1,
            'Required_expertise': 'Expert',
            'Accuracy': 'Low',
            'Sensitivity': 'Low',
            'Complexity': 'High',
            'Robustness': 'Medium'
        },
        'Inputs': [
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_YoungModulus1', 'Name': 'YoungModulus1', 'Description': 'Material Property', 'Units': 'MPa', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_YoungModulus2', 'Name': 'YoungModulus2', 'Description': 'Material Property', 'Units': 'MPa', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_YoungModulus3', 'Name': 'YoungModulus3', 'Description': 'Material Property', 'Units': 'MPa', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_PoissonRatio12', 'Name': 'PoissonRatio12', 'Description': 'Material Property', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_PoissonRatio13', 'Name': 'PoissonRatio13', 'Description': 'Material Property', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_PoissonRatio23', 'Name': 'PoissonRatio23', 'Description': 'Material Property', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_ShearModulus12', 'Name': 'ShearModulus12', 'Description': 'Material Property', 'Units': 'MPa', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_ShearModulus13', 'Name': 'ShearModulus13', 'Description': 'Material Property', 'Units': 'MPa', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_ShearModulus23', 'Name': 'ShearModulus23', 'Description': 'Material Property', 'Units': 'MPa', 'Origin': 'Simulated', 'Required': True}
        ],
        'Outputs': [
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CriticalLoadLevel', 'Name': 'Buckling load', 'Description': 'First buckling load of the analyzed structure', 'Units': 'Nm', 'Origin': 'Simulated'},
            {'Type': 'mupif.Field', 'Type_ID': 'mupif.FieldID.FID_BucklingShape', 'Name': 'Buckling shape', 'Description': 'Three dimensional shape of first buckling load of the analyzed structure', 'Units': 'None', 'Origin': 'Simulated'}
        ]
    },


    # LAMMPS
    {
        'workflowgenerator_classname': 'LAMMPS_API',
        'workflowgenerator_module': '',

        'Name': 'LAMMPS',
        'ID': 'LAMMPS',
        'Description': 'Atomistic simulation for the Airbus case',
        'Physics': {
            'Type': 'Molecular'
        },
        'Solver': {
            'Software': 'LAMMPS',
            'Language': 'C++',
            'License': 'Open-source',
            'Creator': 'Sandia National Labs',
            'Version_date': 'lammps-12dec18',
            'Type': 'Atomistic',
            'Documentation': 'https://lammps.sandia.gov/doc/Manual.html',
            'Estim_time_step_s': 1,
            'Estim_comp_time_s': 0.01,
            'Estim_execution_cost_EUR': 0.01,
            'Estim_personnel_cost_EUR': 0.01,
            'Required_expertise': 'Expert',
            'Accuracy': 'High',
            'Sensitivity': 'High',
            'Complexity': 'High',
            'Robustness': 'High'
        },
        'Inputs': [
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_SMILE_MOLECULAR_STRUCTURE', 'Name': 'Monomer Molecular Structure', 'Description': 'Monomer Molecular Structure', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_MOLECULAR_WEIGHT', 'Name': 'Polymer Molecular Weight', 'Description': 'Polymer Molecular Weight', 'Units': 'mol', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CROSSLINKER_TYPE', 'Name': 'CROSSLINKER TYPE', 'Description': 'CROSSLINKER TYPE', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_FILLER_DESIGNATION', 'Name': 'FILLER DESIGNATION', 'Description': 'FILLER DESIGNATION', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_CROSSLINKONG_DENSITY', 'Name': 'CROSSLINKONG DENSITY', 'Description': 'CROSSLINKONG DENSITY', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_FILLER_CONCENTRATION', 'Name': 'FILLER CONCENTRATION', 'Description': 'FILLER CONCENTRATION', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_TEMPERATURE', 'Name': 'TEMPERATURE', 'Description': 'TEMPERATURE', 'Units': 'degC', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_PRESSURE', 'Name': 'PRESSURE', 'Description': 'TEMPERATURE', 'Units': 'atm', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_POLYDISPERSITY_INDEX', 'Name': 'POLYDISPERSITY INDEX', 'Description': 'POLYDISPERSITY INDEX', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_SMILE_MODIFIER_MOLECULAR_STRUCTURE', 'Name': 'SMILE MODIFIER MOLECULAR STRUCTURE', 'Description': 'SMILE MODIFIER MOLECULAR STRUCTURE', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_SMILE_FILLER_MOLECULAR_STRUCTURE', 'Name': 'SMILE FILLER MOLECULAR STRUCTURE', 'Description': 'SMILE FILLER MOLECULAR STRUCTURE', 'Units': 'None', 'Origin': 'Simulated', 'Required': True},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_DENSITY_OF_FUNCTIONALIZATION', 'Name': 'DENSITY OF FUNCTIONALIZATION', 'Description': 'DENSITY OF FUNCTIONALIZATION', 'Units': 'None', 'Origin': 'Simulated', 'Required': True}
        ],
        'Outputs': [
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_DENSITY', 'Name': 'density', 'Description': 'density', 'Units': 'g/cm^3', 'Origin': 'Simulated'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_EModulus', 'Name': 'Young modulus', 'Description': 'Young modulus', 'Units': 'GPa', 'Origin': 'Simulated'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_effective_conductivity', 'Name': 'Thermal Conductivity', 'Description': 'Thermal Conductivity', 'Units': 'W/m/degC', 'Origin': 'Simulated'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_TRANSITION_TEMPERATURE', 'Name': 'Glass Transition Temperature', 'Description': 'Glass Transition Temperature', 'Units': 'K', 'Origin': 'Simulated'},
            {'Type': 'mupif.Property', 'Type_ID': 'mupif.PropertyID.PID_PoissonRatio', 'Name': 'Poisson Ratio', 'Description': 'Poisson Ratio', 'Units': 'None', 'Origin': 'Simulated'}
        ]
    }

]
