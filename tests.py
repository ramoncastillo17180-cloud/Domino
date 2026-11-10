"""Pruebas deterministas de propagación y reconstrucción de rutas."""
import unittest
from algorithms import bfs, dfs, compare, reconstruct_path


class SearchTests(unittest.TestCase):
    def test_chain(self):
        result = bfs([[1,1,1,1]], (0,0))
        self.assertEqual(list(result.levels.values()), [0,1,2,3])
        self.assertEqual(reconstruct_path(result,(0,3)), [(0,0),(0,1),(0,2),(0,3)])

    def test_branch(self):
        result = bfs([[0,1,0],[1,1,1],[0,1,0]],(1,1))
        self.assertEqual(sorted(result.levels.values()),[0,1,1,1,1])

    def test_isolated_and_blocked(self):
        result = bfs([[1,0,1]],(0,0))
        self.assertEqual(result.order,[(0,0)])
        self.assertEqual(reconstruct_path(result,(0,2)),[])

    def test_cycles_minimum_levels(self):
        matrix = [[1]*4 for _ in range(4)]
        result = bfs(matrix,(0,0))
        for r in range(4):
            for c in range(4): self.assertEqual(result.levels[(r,c)],r+c)
        self.assertEqual(len(result.order),len(set(result.order)))

    def test_obstacle_detour(self):
        result = bfs([[1,0,1],[1,0,1],[1,1,1]],(0,0))
        self.assertEqual(result.levels[(0,2)],6)

    def test_dfs_and_comparison(self):
        matrix = [[1]*3 for _ in range(3)]
        a,b = compare(matrix,(0,0))
        self.assertEqual(set(a.order),set(b.order))
        self.assertEqual(len(b.order),len(set(b.order)))
        self.assertNotEqual(a.order,b.order)
        self.assertEqual(matrix,[[1]*3 for _ in range(3)])
        path = reconstruct_path(b,(2,2))
        self.assertEqual(path[0],(0,0))
        for p,q in zip(path,path[1:]): self.assertEqual(abs(p[0]-q[0])+abs(p[1]-q[1]),1)

    def test_invalid_start(self):
        for matrix,start in [([],None),([[0]],(0,0)),([[1]],None),([[1]],(-1,0)),([[1],[1,1]],(0,0))]:
            with self.assertRaises(ValueError): bfs(matrix,start)


class PlaybackTests(unittest.TestCase):
    def setUp(self):
        from ui import DominoApp
        self.app = DominoApp()
        self.app.withdraw()

    def tearDown(self):
        self.app.close()

    def test_pause_resume_reset(self):
        a = self.app
        a.run()
        self.assertIsNotNone(a.job)
        original = a.job
        a.run()
        self.assertEqual(a.job, original)
        a.pause()
        self.assertIsNone(a.job)
        frozen = dict(a.states)
        a.tick()
        self.assertEqual(a.states, frozen)
        a.resume()
        self.assertIsNotNone(a.job)
        matrix = [row[:] for row in a.matrix]
        a.reset()
        self.assertIsNone(a.job)
        self.assertEqual(a.matrix, matrix)
        self.assertFalse(a.states)

    def test_steps_and_algorithm_change(self):
        a = self.app
        a.step(1)
        first = dict(a.states)
        a.step(1)
        a.step(-1)
        self.assertEqual(a.states, first)
        self.assertIsNone(a.job)
        a.algorithm.set('DFS')
        a.algorithm_changed()
        self.assertIsNone(a.result)
        a.run()
        self.assertEqual(a.result.algorithm, 'DFS')
        a.example()
        self.assertIsNone(a.job)
        self.assertIsNone(a.result)

    def test_parallel_frames_and_finish(self):
        a = self.app
        a.prepare()
        for _ in range(24):
            a.cancel_timer()
            a.tick()
        self.assertTrue(all(a.states[n] == 1 for n in a.groups[1]))
        for _ in range(12*len(a.groups)):
            a.cancel_timer()
            a.tick()
        self.assertFalse(a.running)
        self.assertEqual(set(a.states), set(a.result.order))


class ScenarioTests(unittest.TestCase):
    def test_all_scenarios(self):
        from algorithms import scenario, SCENARIOS
        for name in SCENARIOS:
            m,s,t = scenario(name)
            self.assertTrue(reconstruct_path(bfs(m,s),t))
        m,s,t = scenario(SCENARIOS[-1])
        a,b = compare(m,s,t)
        self.assertLess(len(reconstruct_path(a,t)),len(reconstruct_path(b,t)))
        self.assertEqual(a.order[-1],t)
        self.assertEqual(b.order[-1],t)

    def test_missing_or_unreachable_target(self):
        for result in compare([[1,0,1]],(0,0),(0,2)):
            self.assertEqual(result.order,[(0,0)])
            self.assertEqual(reconstruct_path(result,(0,2)),[])
        for result in compare([[1,1]],(0,0)):
            self.assertEqual(len(result.order),2)
            self.assertEqual(reconstruct_path(result,None),[])

    def test_target_at_start(self):
        for result in compare([[1,1]],(0,0),(0,0)):
            self.assertEqual(result.order,[(0,0)])
            self.assertEqual(reconstruct_path(result,(0,0)),[(0,0)])


class DeliveryChecks(unittest.TestCase):
    def test_bfs_minimum_distances_exhaustive(self):
        """Contrasta BFS con relajación de aristas, sin usar otra cola BFS."""
        for mask in range(1, 512):
            matrix = [[int(bool(mask & (1 << (r*3+c)))) for c in range(3)] for r in range(3)]
            cells = [(r,c) for r in range(3) for c in range(3) if matrix[r][c]]
            for start in cells:
                distances = {node: float('inf') for node in cells}
                distances[start] = 0
                for _ in range(len(cells)-1):
                    for u in cells:
                        for v in cells:
                            if abs(u[0]-v[0])+abs(u[1]-v[1]) == 1:
                                distances[v] = min(distances[v], distances[u]+1)
                expected = {node: value for node,value in distances.items() if value != float('inf')}
                result = bfs(matrix,start)
                self.assertEqual(result.levels,expected)
                self.assertEqual([result.levels[n] for n in result.order],sorted(expected.values()))

    def test_branch_simultaneous_every_frame(self):
        from ui import DominoApp
        a = DominoApp()
        a.withdraw()
        try:
            a.prepare()  # Escenario inicial: bifurcación.
            self.assertTrue(any(len(group)>1 for group in a.groups))
            for index, group in enumerate(a.groups):
                for frame in range(1,13):
                    a.cancel_timer()
                    a.tick()
                    self.assertEqual({a.states[node] for node in group},{frame/12})
                    self.assertTrue(all(a.states[node] == 1 for previous in a.groups[:index] for node in previous))
                    self.assertTrue(all(node not in a.states for future in a.groups[index+1:] for node in future))
        finally:
            a.close()

    def test_table_displays_actual_calculations(self):
        from unittest.mock import patch
        from tkinter import Toplevel, ttk
        from ui import DominoApp
        from algorithms import SCENARIOS
        a = DominoApp()
        a.withdraw()
        observed = []
        try:
            for name in (SCENARIOS[0], SCENARIOS[-1]):
                a.preset.set(name)
                a.example()
                actual = []
                def record(*args):
                    results = compare(*args)
                    actual.extend(results)
                    return results
                # Envolver, sin sustituir los algoritmos ni sus mediciones.
                with patch('ui.compare',side_effect=record) as call:
                    a.comparison()
                    call.assert_called_once_with(a.matrix,a.start,a.target)
                win = [w for w in a.winfo_children() if isinstance(w,Toplevel)][-1]
                table = next(w for w in win.winfo_children() if isinstance(w,ttk.Treeview))
                rows = [table.item(item,'values') for item in table.get_children()]
                for row,result in zip(rows,actual):
                    self.assertEqual(int(row[2]),len(result.order))
                    self.assertEqual(int(row[3]),len(reconstruct_path(result,a.target))-1)
                    self.assertEqual(row[4],f'{result.seconds*1000:.4f}')
                    self.assertEqual(result.order[-1],a.target)
                observed.append(tuple(row[3] for row in rows))
                win.destroy()
            self.assertNotEqual(observed[0],observed[1])
        finally:
            a.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
