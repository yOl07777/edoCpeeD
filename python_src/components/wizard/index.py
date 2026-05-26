from __future__ import annotations

from python_src.components.wizard.WizardDialogLayout import WizardDialogLayout
from python_src.components.wizard.WizardNavigationFooter import WizardNavigationFooter
from python_src.components.wizard.WizardProvider import WizardContext, WizardProvider
from python_src.components.wizard.useWizard import useWizard


default = {"provider": "deepseek", "components": ["WizardProvider", "WizardDialogLayout", "WizardNavigationFooter"]}


__all__ = ["WizardContext", "WizardDialogLayout", "WizardNavigationFooter", "WizardProvider", "default", "useWizard"]
