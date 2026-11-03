from typing import List, Dict

from ..game.SkillDetails import SkillDetails


class SkillData:
    SKILLS_BY_SKILL_TREE: Dict[int, List[SkillDetails]] = {
        1: [
            SkillDetails(0, 63, 0, 1, 1, 0),
            SkillDetails(1, 0, 10, 2, 2, 0),
            SkillDetails(2, 64, 0, 1, 1, 0),
            SkillDetails(3, 0, 3, 3, 3, 0),
            SkillDetails(4, 65, 0, 1, 1, 0),
            SkillDetails(5, 0, 20, 2, 2, 0),
            SkillDetails(6, 66, 0, 1, 1, 0),
            SkillDetails(7, 0, 30, 2, 2, 0),
            SkillDetails(8, 67, 0, 1, 1, 0),
            SkillDetails(9, 0, 0, 5, 4, 0),
            SkillDetails(10, 68, 0, 1, 1, 0)
        ],
        2: [
            SkillDetails(12, 69, 0, 1, 1, 0),
            SkillDetails(11, 0, 10, 2, 2, 0),
            SkillDetails(14, 70, 0, 1, 1, 0),
            SkillDetails(16, 71, 0, 1, 1, 0),
            SkillDetails(13, 0, 3, 3, 3, 0),
            SkillDetails(15, 0, 20, 2, 2, 0),
            SkillDetails(18, 72, 0, 1, 1, 0),
            SkillDetails(17, 0, 30, 2, 2, 0),
            SkillDetails(19, 73, 0, 1, 1, 0),
            SkillDetails(20, 0, 0, 5, 4, 0),
            SkillDetails(21, 74, 0, 1, 1, 0)
        ],
        3: [
            SkillDetails(22, 75, 0, 1, 1, 0),
            SkillDetails(23, 0, 10, 2, 2, 0),
            SkillDetails(24, 76, 0, 1, 1, 0),
            SkillDetails(27, 0, 3, 3, 3, 0),
            SkillDetails(26, 77, 0, 1, 1, 0),
            SkillDetails(25, 0, 20, 2, 2, 0),
            SkillDetails(28, 78, 0, 1, 1, 0),
            SkillDetails(29, 0, 30, 2, 2, 0),
            SkillDetails(30, 79, 0, 1, 1, 0),
            SkillDetails(31, 0, 0, 5, 4, 0),
            SkillDetails(32, 80, 0, 1, 1, 0)
        ],
        4: [
            SkillDetails(55, 0, 10, 2, 12, 0),
            SkillDetails(56, 81, 0, 1, 1, 0),
            SkillDetails(57, 0, 2, 11, 13, 0),
            SkillDetails(58, 82, 0, 1, 1, 0),
            SkillDetails(59, 0, 30, 2, 12, 0),
            SkillDetails(60, 83, 0, 1, 1, 0),
            SkillDetails(61, 0, 4, 12, 13, 0),
            SkillDetails(62, 0, 60, 2, 12, 0),
            SkillDetails(63, 0, 0, 13, 0, 0),
            SkillDetails(64, 0, 0, 5, 4, 0),
            SkillDetails(65, 84, 0, 1, 1, 0)
        ],
        5: [
            SkillDetails(88, 85, 0, 1, 1, 0),
            SkillDetails(90, 86, 0, 1, 1, 0),
            SkillDetails(89, 0, 10, 2, 2, 0),
            SkillDetails(94, 88, 0, 1, 1, 0),
            SkillDetails(91, 0, 20, 2, 2, 0),
            SkillDetails(92, 87, 0, 1, 1, 0),
            SkillDetails(93, 0, 30, 2, 2, 0),
            SkillDetails(95, 89, 0, 1, 1, 0),
            SkillDetails(96, 90, 0, 1, 1, 0),
            SkillDetails(97, 0, 0, 5, 4, 0),
            SkillDetails(98, 91, 0, 1, 1, 0)
        ],
        6: [
            SkillDetails(66, 0, 10, 2, 2, 0),
            SkillDetails(67, 92, 0, 1, 1, 0),
            SkillDetails(70, 0, 3, 3, 3, 0),
            SkillDetails(69, 93, 0, 1, 1, 0),
            SkillDetails(68, 0, 20, 2, 2, 0),
            SkillDetails(71, 94, 0, 1, 1, 0),
            SkillDetails(72, 0, 4, 14, 14, 0),
            SkillDetails(73, 95, 0, 1, 1, 0),
            SkillDetails(74, 0, 30, 2, 2, 0),
            SkillDetails(75, 0, 0, 5, 4, 0),
            SkillDetails(76, 96, 0, 1, 1, 0)
        ],
        7: [
            SkillDetails(110, 97, 0, 1, 1, 0),
            SkillDetails(111, 0, 10, 2, 2, 0),
            SkillDetails(112, 98, 0, 1, 1, 0),
            SkillDetails(113, 0, 3, 3, 3, 0),
            SkillDetails(114, 99, 0, 1, 1, 0),
            SkillDetails(115, 0, 20, 2, 2, 0),
            SkillDetails(116, 100, 0, 1, 1, 0),
            SkillDetails(117, 0, 30, 2, 2, 0),
            SkillDetails(118, 101, 0, 1, 1, 0),
            SkillDetails(119, 0, 0, 5, 4, 0),
            SkillDetails(120, 102, 0, 1, 1, 0)
        ],
        8: [
            SkillDetails(122, 103, 0, 1, 1, 0),
            SkillDetails(121, 0, 10, 2, 2, 0),
            SkillDetails(124, 104, 0, 1, 1, 0),
            SkillDetails(125, 0, 3, 3, 3, 0),
            SkillDetails(126, 105, 0, 1, 1, 0),
            SkillDetails(123, 0, 20, 2, 2, 0),
            SkillDetails(128, 106, 0, 1, 1, 0),
            SkillDetails(127, 0, 30, 2, 2, 0),
            SkillDetails(129, 107, 0, 1, 1, 0),
            SkillDetails(130, 0, 0, 5, 4, 0),
            SkillDetails(131, 108, 0, 1, 1, 0)
        ],
        9: [
            SkillDetails(178, 110, 0, 1, 1, 0),
            SkillDetails(177, 0, 10, 2, 2, 0),
            SkillDetails(180, 111, 0, 1, 1, 0),
            SkillDetails(181, 0, 3, 3, 3, 0),
            SkillDetails(176, 109, 0, 1, 1, 0),
            SkillDetails(179, 0, 20, 2, 2, 0),
            SkillDetails(182, 112, 0, 1, 1, 0),
            SkillDetails(183, 0, 30, 2, 2, 0),
            SkillDetails(184, 113, 0, 1, 1, 0),
            SkillDetails(185, 0, 0, 5, 4, 0),
            SkillDetails(186, 114, 0, 1, 1, 0)
        ],
        10: [
            SkillDetails(188, 115, 0, 1, 1, 0),
            SkillDetails(187, 0, 10, 2, 2, 0),
            SkillDetails(190, 116, 0, 1, 1, 0),
            SkillDetails(189, 0, 3, 3, 3, 0),
            SkillDetails(192, 117, 0, 1, 1, 0),
            SkillDetails(191, 0, 20, 2, 2, 0),
            SkillDetails(194, 118, 0, 1, 1, 0),
            SkillDetails(193, 0, 30, 2, 2, 0),
            SkillDetails(195, 119, 0, 1, 1, 0),
            SkillDetails(196, 0, 0, 5, 4, 0),
            SkillDetails(197, 120, 0, 1, 1, 0)
        ],
        11: [
            SkillDetails(242, 121, 0, 1, 1, 0),
            SkillDetails(244, 122, 0, 1, 1, 0),
            SkillDetails(243, 0, 10, 2, 2, 0),
            SkillDetails(246, 123, 0, 1, 1, 0),
            SkillDetails(245, 0, 20, 2, 2, 0),
            SkillDetails(248, 124, 0, 1, 1, 0),
            SkillDetails(249, 125, 0, 1, 1, 0),
            SkillDetails(247, 0, 30, 2, 2, 0),
            SkillDetails(250, 126, 0, 1, 1, 0),
            SkillDetails(251, 0, 0, 5, 4, 0),
            SkillDetails(252, 127, 0, 1, 1, 0)
        ],
        12: [
            SkillDetails(210, 128, 0, 1, 1, 0),
            SkillDetails(209, 0, 10, 2, 2, 0),
            SkillDetails(212, 129, 0, 1, 1, 0),
            SkillDetails(213, 0, 3, 3, 3, 0),
            SkillDetails(214, 130, 0, 1, 1, 0),
            SkillDetails(211, 0, 20, 2, 2, 0),
            SkillDetails(216, 131, 0, 1, 1, 0),
            SkillDetails(215, 0, 30, 2, 2, 0),
            SkillDetails(217, 132, 0, 1, 1, 0),
            SkillDetails(218, 0, 0, 5, 4, 0),
            SkillDetails(219, 133, 0, 1, 1, 0)
        ],
        13: [
            SkillDetails(33, 134, 0, 1, 1, 0),
            SkillDetails(34, 0, 2, 6, 5, 0),
            SkillDetails(35, 135, 0, 1, 1, 0),
            SkillDetails(36, 0, 2, 7, 5, 0),
            SkillDetails(37, 136, 0, 1, 1, 0),
            SkillDetails(39, 137, 0, 1, 1, 0),
            SkillDetails(38, 0, 2, 8, 5, 0),
            SkillDetails(43, 139, 0, 1, 1, 0),
            SkillDetails(41, 138, 0, 1, 1, 0),
            SkillDetails(42, 0, 0, 5, 4, 0),
            SkillDetails(40, 0, 0, 9, 0, 0)
        ],
        14: [
            SkillDetails(133, 140, 0, 1, 1, 0),
            SkillDetails(132, 0, 10, 16, 2, 0),
            SkillDetails(135, 141, 0, 1, 1, 0),
            SkillDetails(134, 0, 3, 3, 3, 0),
            SkillDetails(137, 142, 0, 1, 1, 0),
            SkillDetails(136, 0, 4, 17, 14, 0),
            SkillDetails(139, 143, 0, 1, 1, 0),
            SkillDetails(138, 0, 30, 16, 2, 0),
            SkillDetails(140, 144, 0, 1, 1, 0),
            SkillDetails(141, 0, 60, 16, 2, 0),
            SkillDetails(142, 145, 0, 1, 1, 0)
        ],
        15: [
            SkillDetails(44, 146, 0, 1, 1, 0),
            SkillDetails(45, 0, 10, 4, 6, 0),
            SkillDetails(46, 147, 0, 1, 1, 207),
            SkillDetails(47, 0, 20, 4, 7, 0),
            SkillDetails(48, 148, 0, 1, 1, 0),
            SkillDetails(49, 0, 30, 4, 6, 0),
            SkillDetails(50, 149, 0, 1, 1, 0),
            SkillDetails(51, 0, 40, 4, 7, 0),
            SkillDetails(52, 0, 60, 4, 11, 0),
            SkillDetails(53, 150, 0, 1, 1, 0),
            SkillDetails(54, 0, 0, 10, 0, 0)
        ],
        16: [
            SkillDetails(77, 208, 0, 1, 1, 208),
            SkillDetails(78, 0, 20, 4, 15, 0),
            SkillDetails(79, 209, 0, 1, 1, 209),
            SkillDetails(80, 0, 10, 4, 12, 0),
            SkillDetails(81, 153, 0, 1, 1, 0),
            SkillDetails(82, 0, 60, 4, 15, 0),
            SkillDetails(83, 152, 0, 1, 1, 0),
            SkillDetails(84, 0, 20, 4, 12, 0),
            SkillDetails(85, 151, 0, 1, 1, 0),
            SkillDetails(86, 0, 100, 4, 15, 0),
            SkillDetails(87, 154, 0, 1, 1, 0)
        ],
        17: [
            SkillDetails(102, 156, 0, 1, 1, 0),
            SkillDetails(99, 0, 20, 4, 16, 0),
            SkillDetails(100, 155, 0, 1, 1, 0),
            SkillDetails(101, 0, 10, 4, 12, 0),
            SkillDetails(104, 157, 0, 1, 1, 0),
            SkillDetails(103, 0, 3, 15, 17, 0),
            SkillDetails(106, 158, 0, 1, 1, 0),
            SkillDetails(107, 0, 60, 4, 16, 0),
            SkillDetails(105, 0, 20, 4, 12, 0),
            SkillDetails(108, 0, 100, 4, 16, 0),
            SkillDetails(109, 159, 0, 1, 1, 0)
        ],
        18: [
            SkillDetails(143, 160, 0, 1, 1, 0),
            SkillDetails(144, 0, 10, 4, 8, 0),
            SkillDetails(145, 161, 0, 1, 1, 0),
            SkillDetails(146, 0, 10, 4, 6, 0),
            SkillDetails(147, 162, 0, 1, 1, 162),
            SkillDetails(148, 0, 30, 4, 11, 0),
            SkillDetails(149, 163, 0, 1, 1, 0),
            SkillDetails(150, 0, 30, 4, 8, 0),
            SkillDetails(151, 164, 0, 1, 1, 164),
            SkillDetails(152, 0, 60, 4, 8, 0),
            SkillDetails(153, 0, 0, 18, 0, 0)
        ],
        19: [
            SkillDetails(154, 0, 20, 4, 9, 0),
            SkillDetails(155, 165, 0, 1, 1, 0),
            SkillDetails(156, 0, 20, 4, 8, 0),
            SkillDetails(157, 210, 0, 1, 1, 210),
            SkillDetails(158, 0, 20, 4, 11, 0),
            SkillDetails(159, 211, 0, 1, 1, 211),
            SkillDetails(160, 0, 40, 4, 9, 0),
            SkillDetails(161, 166, 0, 1, 1, 0),
            SkillDetails(162, 0, 40, 4, 8, 0),
            SkillDetails(163, 213, 0, 1, 1, 213),
            SkillDetails(164, 0, 0, 19, 0, 0)
        ],
        20: [
            SkillDetails(165, 167, 0, 1, 1, 0),
            SkillDetails(166, 0, 0, 20, 14, 0),
            SkillDetails(167, 169, 0, 1, 1, 0),
            SkillDetails(168, 0, 30, 4, 10, 0),
            SkillDetails(169, 171, 0, 1, 1, 0),
            SkillDetails(170, 0, 30, 4, 16, 0),
            SkillDetails(171, 803, 0, 1, 1, 0),
            SkillDetails(172, 0, 30, 4, 15, 0),
            SkillDetails(173, 804, 0, 1, 1, 0),
            SkillDetails(174, 0, 50, 4, 9, 0),
            SkillDetails(175, 196, 0, 1, 1, 0)
        ],
        21: [
            SkillDetails(198, 0, 10, 4, 11, 0),
            SkillDetails(199, 172, 0, 1, 1, 0),
            SkillDetails(200, 0, 10, 4, 6, 0),
            SkillDetails(201, 173, 0, 1, 1, 0),
            SkillDetails(202, 0, 20, 4, 11, 0),
            SkillDetails(205, 175, 0, 1, 1, 0),
            SkillDetails(204, 0, 30, 4, 6, 0),
            SkillDetails(203, 174, 0, 1, 1, 0),
            SkillDetails(206, 0, 30, 4, 11, 0),
            SkillDetails(207, 176, 0, 1, 1, 0),
            SkillDetails(208, 0, 0, 21, 0, 0)
        ],
        22: [
            SkillDetails(220, 177, 0, 1, 1, 0),
            SkillDetails(221, 0, 10, 4, 6, 0),
            SkillDetails(222, 178, 0, 1, 1, 0),
            SkillDetails(223, 0, 20, 4, 7, 0),
            SkillDetails(224, 179, 0, 1, 1, 0),
            SkillDetails(225, 0, 10, 4, 10, 0),
            SkillDetails(226, 180, 0, 1, 1, 0),
            SkillDetails(227, 0, 30, 4, 16, 0),
            SkillDetails(228, 181, 0, 1, 1, 0),
            SkillDetails(229, 0, 30, 4, 11, 0),
            SkillDetails(230, 0, 0, 1, 1, 0)
        ],
        23: [
            SkillDetails(231, 476, 0, 1, 1, 0),
            SkillDetails(232, 0, 10, 4, 7, 0),
            SkillDetails(233, 183, 0, 1, 1, 0),
            SkillDetails(234, 0, 30, 4, 15, 0),
            SkillDetails(235, 184, 0, 1, 1, 0),
            SkillDetails(236, 0, 30, 4, 7, 0),
            SkillDetails(237, 185, 0, 1, 1, 0),
            SkillDetails(238, 0, 60, 4, 7, 0),
            SkillDetails(239, 182, 0, 1, 1, 0),
            SkillDetails(240, 0, 80, 4, 11, 0),
            SkillDetails(241, 187, 0, 1, 1, 0)
        ],
        24: [
            SkillDetails(253, 0, 20, 4, 15, 0),
            SkillDetails(254, 215, 0, 1, 1, 215),
            SkillDetails(255, 0, 20, 4, 16, 0),
            SkillDetails(256, 188, 0, 1, 1, 0),
            SkillDetails(257, 0, 40, 4, 15, 0),
            SkillDetails(258, 189, 0, 1, 1, 0),
            SkillDetails(259, 0, 40, 4, 16, 0),
            SkillDetails(260, 190, 0, 1, 1, 0),
            SkillDetails(261, 0, 60, 4, 12, 0),
            SkillDetails(262, 0, 0, 22, 0, 0),
            SkillDetails(263, 533, 0, 1, 1, 0)
        ],
        25: [
            SkillDetails(264, 0, 10, 4, 10, 0),
            SkillDetails(265, 477, 0, 1, 1, 0),
            SkillDetails(266, 0, 20, 4, 8, 0),
            SkillDetails(267, 191, 0, 1, 1, 0),
            SkillDetails(268, 0, 20, 4, 11, 0),
            SkillDetails(269, 192, 0, 1, 1, 0),
            SkillDetails(270, 0, 20, 4, 10, 0),
            SkillDetails(271, 194, 0, 1, 1, 0),
            SkillDetails(272, 0, 30, 4, 10, 0),
            SkillDetails(273, 195, 0, 1, 1, 0),
            SkillDetails(274, 479, 0, 1, 1, 0)
        ],
        26: [
            SkillDetails(277, 198, 0, 1, 1, 0),
            SkillDetails(276, 0, 10, 4, 9, 0),
            SkillDetails(275, 197, 0, 1, 1, 0),
            SkillDetails(278, 0, 20, 4, 8, 0),
            SkillDetails(279, 199, 0, 1, 1, 217),
            SkillDetails(280, 0, 20, 4, 7, 0),
            SkillDetails(281, 200, 0, 1, 1, 0),
            SkillDetails(282, 0, 30, 4, 9, 0),
            SkillDetails(283, 201, 0, 1, 1, 0),
            SkillDetails(284, 0, 60, 4, 9, 0),
            SkillDetails(285, 0, 0, 23, 3, 0)
        ]
    }

    @staticmethod
    def get_skills_by_skill_tree(skill_tree: int) -> list[SkillDetails]:
        if skill_tree not in SkillData.SKILLS_BY_SKILL_TREE:
            raise "Invalid skill tree {} provided - this should not happen!".format(skill_tree)
        return SkillData.SKILLS_BY_SKILL_TREE[skill_tree]

    @staticmethod
    def get_all_skills() -> List[SkillDetails]:
        all_skills = []
        for skills in SkillData.SKILLS_BY_SKILL_TREE.values():
            all_skills.extend(skills)
        return all_skills
