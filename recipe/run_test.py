"""
RDKit smoke tests — verify core functionality of the installed package.
"""
import unittest
import sys


class TestSmilesAndMolBasics(unittest.TestCase):

    def test_import_and_version(self):
        from rdkit import Chem, rdBase
        self.assertTrue(hasattr(rdBase, 'rdkitVersion'))
        mol = Chem.MolFromSmiles('C')
        self.assertIsNotNone(mol)

    def test_smiles_roundtrip(self):
        from rdkit import Chem
        smi = 'c1ccc(O)cc1'
        mol = Chem.MolFromSmiles(smi)
        self.assertIsNotNone(mol)
        canon = Chem.MolToSmiles(mol)
        mol2 = Chem.MolFromSmiles(canon)
        self.assertEqual(Chem.MolToSmiles(mol2), canon)

    def test_smarts_substructure(self):
        from rdkit import Chem
        mol = Chem.MolFromSmiles('c1ccc(NC(=O)C)cc1')
        pattern = Chem.MolFromSmarts('[NX3][CX3](=O)')
        self.assertTrue(mol.HasSubstructMatch(pattern))
        matches = mol.GetSubstructMatches(pattern)
        self.assertGreaterEqual(len(matches), 1)

    def test_atom_bond_properties(self):
        from rdkit import Chem
        mol = Chem.MolFromSmiles('CCO')
        self.assertEqual(mol.GetNumAtoms(), 3)
        self.assertEqual(mol.GetNumBonds(), 2)
        oxygen = mol.GetAtomWithIdx(2)
        self.assertEqual(oxygen.GetAtomicNum(), 8)
        self.assertEqual(oxygen.GetSymbol(), 'O')
        bond = mol.GetBondBetweenAtoms(0, 1)
        self.assertEqual(bond.GetBondType(), Chem.BondType.SINGLE)


class TestDescriptors(unittest.TestCase):

    def test_molecular_weight_and_logp(self):
        from rdkit import Chem
        from rdkit.Chem import Descriptors
        mol = Chem.MolFromSmiles('c1ccccc1')  # benzene
        mw = Descriptors.ExactMolWt(mol)
        self.assertAlmostEqual(mw, 78.047, places=2)
        logp = Descriptors.MolLogP(mol)
        self.assertIsInstance(logp, float)

    def test_molecular_formula(self):
        from rdkit.Chem import AllChem, MolFromSmiles
        mol = MolFromSmiles('C1CCCCC1')
        formula = AllChem.CalcMolFormula(mol)
        self.assertEqual(formula, 'C6H12')

    def test_tpsa_and_rotatable_bonds(self):
        from rdkit import Chem
        from rdkit.Chem import Descriptors
        mol = Chem.MolFromSmiles('CC(=O)Oc1ccccc1C(=O)O')  # aspirin
        tpsa = Descriptors.TPSA(mol)
        self.assertGreater(tpsa, 0)
        nrot = Descriptors.NumRotatableBonds(mol)
        self.assertGreaterEqual(nrot, 2)


class TestFingerprints(unittest.TestCase):

    def test_morgan_fingerprint(self):
        from rdkit import Chem
        from rdkit.Chem import rdFingerprintGenerator
        mol = Chem.MolFromSmiles('c1ccccc1')
        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        fp = gen.GetFingerprint(mol)
        self.assertEqual(fp.GetNumBits(), 2048)
        self.assertGreater(fp.GetNumOnBits(), 0)

    def test_rdkit_fingerprint(self):
        from rdkit import Chem
        fp = Chem.RDKFingerprint(Chem.MolFromSmiles('CCO'))
        self.assertEqual(fp.GetNumBits(), 2048)
        self.assertGreater(fp.GetNumOnBits(), 0)

    def test_tanimoto_similarity(self):
        from rdkit import Chem, DataStructs
        from rdkit.Chem import rdFingerprintGenerator
        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        fp1 = gen.GetFingerprint(Chem.MolFromSmiles('c1ccccc1'))
        fp2 = gen.GetFingerprint(Chem.MolFromSmiles('c1ccc(O)cc1'))
        sim = DataStructs.TanimotoSimilarity(fp1, fp2)
        self.assertGreater(sim, 0.0)
        self.assertLessEqual(sim, 1.0)
        self.assertEqual(DataStructs.TanimotoSimilarity(fp1, fp1), 1.0)


class TestCoordinatesAndForceField(unittest.TestCase):

    def test_2d_coords(self):
        from rdkit import Chem
        from rdkit.Chem import AllChem
        mol = Chem.MolFromSmiles('c1ccccc1')
        AllChem.Compute2DCoords(mol)
        conf = mol.GetConformer()
        self.assertEqual(conf.GetNumAtoms(), mol.GetNumAtoms())

    def test_3d_embed(self):
        from rdkit import Chem
        from rdkit.Chem import AllChem
        mol = Chem.AddHs(Chem.MolFromSmiles('CCO'))
        result = AllChem.EmbedMolecule(mol, randomSeed=42)
        self.assertEqual(result, 0)
        self.assertEqual(mol.GetNumConformers(), 1)

    def test_force_field_mmff(self):
        from rdkit import Chem
        from rdkit.Chem import AllChem
        mol = Chem.AddHs(Chem.MolFromSmiles('CCCC'))
        AllChem.EmbedMolecule(mol, randomSeed=42)
        res = AllChem.MMFFOptimizeMolecule(mol, maxIters=200)
        self.assertIn(res, (0, 1))


class TestReactionsAndIO(unittest.TestCase):

    def test_reaction_smarts(self):
        from rdkit.Chem import AllChem
        rxn = AllChem.ReactionFromSmarts('[C:1](=O)[OH].[N:2]>>[C:1](=O)[N:2]')
        self.assertIsNotNone(rxn)
        self.assertEqual(rxn.GetNumReactantTemplates(), 2)
        self.assertEqual(rxn.GetNumProductTemplates(), 1)

    def test_mol_block_roundtrip(self):
        from rdkit import Chem
        mol = Chem.MolFromSmiles('c1ccc(N)cc1')
        Chem.AllChem.Compute2DCoords(mol)
        block = Chem.MolToMolBlock(mol)
        self.assertIn('V2000', block)
        mol2 = Chem.MolFromMolBlock(block)
        self.assertIsNotNone(mol2)
        self.assertEqual(mol2.GetNumAtoms(), mol.GetNumAtoms())

    def test_inchi(self):
        from rdkit import Chem
        from rdkit.Chem import INCHI_AVAILABLE
        if not INCHI_AVAILABLE:
            self.skipTest('InChI not available')
        mol = Chem.MolFromSmiles('CCO')
        inchi = Chem.MolToInchi(mol)
        self.assertTrue(inchi.startswith('InChI='))
        key = Chem.InchiToInchiKey(inchi)
        self.assertEqual(len(key), 27)


class TestChemUtils(unittest.TestCase):

    def test_murcko_scaffold(self):
        from rdkit import Chem
        from rdkit.Chem.Scaffolds import MurckoScaffold
        mol = Chem.MolFromSmiles('c1ccc(CC2CCCCC2)cc1')
        core = MurckoScaffold.GetScaffoldForMol(mol)
        self.assertIsNotNone(core)
        framework = MurckoScaffold.MakeScaffoldGeneric(core)
        self.assertGreater(framework.GetNumAtoms(), 0)

    def test_salt_remover(self):
        from rdkit import Chem
        from rdkit.Chem.SaltRemover import SaltRemover
        remover = SaltRemover()
        mol = Chem.MolFromSmiles('CC(=O)[O-].[Na+]')
        stripped = remover.StripMol(mol)
        self.assertLess(stripped.GetNumAtoms(), mol.GetNumAtoms())

    def test_draw_mol_to_image(self):
        from rdkit import Chem
        from rdkit.Chem.Draw import rdMolDraw2D
        mol = Chem.MolFromSmiles('c1ccccc1')
        drawer = rdMolDraw2D.MolDraw2DSVG(300, 300)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        self.assertIn('<svg', svg)
        self.assertGreater(len(svg), 100)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.TestLoader().loadTestsFromModule(sys.modules[__name__]))
    sys.exit(0 if result.wasSuccessful() else 1)
