"""
Inverse kinematic class in pyosim
"""
from pathlib import Path

import opensim as osim


class IK:
    """
    Inverse kinematic in pyosim

    Parameters
    ----------
    model_input : str
        Path to the generic model
    xml_input : str
        Path to the generic scaling xml
    xml_output : str
        Output path of the scaling xml
    trc : str, Path, list
        Path or list of path to the marker files (`.trc`)
    mot_output : Path, str
        Output directory
    onsets : dict, optional
        Dictionary which contains the starting and ending point in second as values and trial name as keys
    prefix : str, optional
        Optional prefix to put in front of the output filename (typically model name)

    Examples
    --------

    >>> from pyosim import Conf
    >>> from pyosim import IK
    >>> participant = 'dapo'
    >>> model = 'wu'
    >>> PROJECT_PATH = Path('../Misc/project_sample')

    >>> trials = [ifile for ifile in (PROJECT_PATH / participant / '0_markers').glob('*.trc')]
    >>> conf = Conf(project_path=PROJECT_PATH)
    >>> onsets = conf.get_conf_field(participant, ['onset'])

    >>> ik = IK(
    >>>     model_input=f"{PROJECT_PATH / iparticipant / '_models' / imodel}_scaled_markers.osim",
    >>>     xml_input=f'{TEMPLATES_PATH / imodel}_ik.xml',
    >>>     xml_output=f"{PROJECT_PATH / iparticipant / '_xml' / imodel}_ik.xml",
    >>>     trc=trials,
    >>>     mot_output=f"{PROJECT_PATH / iparticipant / '1_inverse_kinematic'}",
    >>>     onsets=onsets,
    >>>     prefix=model
    >>> )
    """

    def __init__(self, model_input, xml_input, xml_output, trc, mot_output, onsets=None, prefix=None):
        self.model = osim.Model(model_input)
        self.mot_output = mot_output
        self.onsets = onsets
        self.xml_output = xml_output
        if prefix:
            self.prefix = prefix

        if not isinstance(trc, list):
            self.trc = [trc]
        else:
            self.trc = trc

        if not isinstance(self.trc[0], Path):
            self.trc = [Path(i) for i in self.trc]

        # initialize inverse kinematic tool from setup file
        self.ik_tool = osim.InverseKinematicsTool(xml_input)
        self.ik_tool.setModel(self.model)

        self.run_ik_tool()

    def run_ik_tool(self):
        for ifile in self.trc:
            print(f'\t{ifile.stem}')

            # set name of input (trc) file and output (mot)
            if self.prefix:
                filename = f"{self.prefix}_{ifile.stem}"
            else:
                filename = ifile.stem
            self.ik_tool.setName(filename)
            self.ik_tool.setMarkerDataFileName(f'{ifile}')
            self.ik_tool.setOutputMotionFileName(f"{Path(self.mot_output) / filename}.mot")
            self.ik_tool.setResultsDir(self.mot_output)

            if ifile.stem in self.onsets:
                # set start and end times from configuration file
                start = self.onsets[ifile.stem][0]
                end = self.onsets[ifile.stem][1]
            else:
                # use the trc file to get the start and end times
                m = osim.MarkerData(f'{ifile}')
                start = m.getStartFrameTime()
                end = m.getLastFrameTime() - 1e-2  # -1e-2 because remove last frame resolves some bug
            self.ik_tool.setStartTime(start)
            self.ik_tool.setEndTime(end)

            self.ik_tool.printToXML(self.xml_output)
            self.ik_tool.run()
