import os
import numpy as np

from desilike.theories.galaxy_clustering import (KaiserTracerPowerSpectrumMultipoles, LPTVelocileptorsTracerPowerSpectrumMultipoles,
                                                 DirectPowerSpectrumTemplate, ShapeFitPowerSpectrumTemplate)
from desilike.emulators import Emulator, EmulatedCalculator, CollectionCalculator
from desilike import setup_logging


def test_base():
    emulator_dir = '_tests'
    fn = os.path.join(emulator_dir, 'emu.npy')

    for Template in [DirectPowerSpectrumTemplate, ShapeFitPowerSpectrumTemplate]:

        template = Template()
        calculator = KaiserTracerPowerSpectrumMultipoles(template=template)
        template.params['fsigma8'] = {'derived': True}
        calculator.all_params['b1'].update(derived='{b}**2', prior=None)
        calculator.all_params['b'] = {'prior': {'limits': [0., 2.]}}
        emulator = Emulator(calculator, engine='point')
        emulator.set_samples()
        emulator.fit()
        emulator.save(fn)
        emulator = emulator.to_calculator()
        emulator = EmulatedCalculator.load(fn)
        #emulator.runtime_info.initialize()
        #print(emulator.runtime_info.input_values)
        #print(emulator.varied_params, emulator.all_params)
        #print(emulator.runtime_info.pipeline.get_cosmo_requires())
        emulator()
        emulator = emulator.deepcopy()
        #print(emulator.params, emulator.runtime_info.init[2], emulator.runtime_info.params)
        emulator().shape
        emulator.save(fn)
        emulator = EmulatedCalculator.load(fn)

        template = Template()
        calculator = KaiserTracerPowerSpectrumMultipoles(template=template)
        template.init.params['fsigma8'] = {'derived': True}
        calculator = CollectionCalculator([calculator, calculator.deepcopy()])
        calculator.all_params['b1'].update(derived='{b}**2', prior=None)
        calculator.all_params['b'] = {'prior': {'limits': [0., 2.]}}
        emulator = Emulator(calculator, engine='point')
        emulator.set_samples()
        emulator.fit()
        emulator.save(fn)
        emulators = emulator.to_calculator()
        assert emulators[0].fsigma8.shape == ()
        assert np.allclose(emulators[1](), emulators[0]())
        emulators = EmulatedCalculator.load(fn)
        assert np.allclose(emulators[1](), emulators[0]())
        emulators[0].save(fn)
        emulator = EmulatedCalculator.load(fn)
        assert np.allclose(emulator(), emulators[0]())

    calculator = LPTVelocileptorsTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate())
    calculator()
    pt = calculator.pt
    emulator = Emulator(pt, engine='point')
    emulator.set_samples()
    emulator.fit()
    emulator.save(fn)
    pt = EmulatedCalculator.load(fn)
    calculator.init.update(pt=pt)
    pt.params['df'].update(prior=None, derived='.auto')
    print(calculator.varied_params)
    calculator(dm=0.01)
    print(calculator.varied_params)


def test_backward():
    emulator_dir = '_tests'
    fn = os.path.join(emulator_dir, 'emulator_rept.npy')
    pt = EmulatedCalculator.load(fn)
    pt()


if __name__ == '__main__':

    setup_logging()
    test_base()
    test_backward()
