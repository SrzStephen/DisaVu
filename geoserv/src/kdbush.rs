/*
 * Copyright (c) 2017, Pirmin Kalberer <https://github.com/pka/rust-kdbush>,
 *               2022, Rico A. Beti
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

use std::cmp;
use std::f64;

type TIndex = usize;
type TNumber = f64;
type Point = [TNumber; 2];

pub const DEFAULT_NODE_SIZE: u8 = 64;

/// Input points reader trait
///
/// # Example
///
/// ```
/// struct Points { points: Vec<(f64, f64)> };
/// impl geoserv::kdbush::PointReader for Points {
///    fn size_hint(&self) -> usize {
///        self.points.len()
///    }
///    fn visit_all<F>(&self, mut visitor: F)
///        where F: FnMut(usize, f64, f64)
///    {
///        for (i, point) in self.points.iter().enumerate() {
///            visitor(i, point.0, point.1);
///        }
///    }
/// }
/// ```
pub trait PointReader {
    fn size_hint(&self) -> usize;
    fn visit_all<F>(&self, visitor: F)
    where
        F: FnMut(usize, f64, f64);
}

impl PointReader for Vec<(f64, f64)> {
    fn size_hint(&self) -> usize {
        self.len()
    }
    fn visit_all<F>(&self, mut visitor: F)
    where
        F: FnMut(usize, f64, f64),
    {
        for (i, point) in self.iter().enumerate() {
            visitor(i, point.0, point.1);
        }
    }
}

/// A very fast static spatial index for 2D points based on a flat KD-tree
pub struct KDBush {
    ids: Vec<TIndex>,
    points: Vec<Point>,
    node_size: u8,
}

impl KDBush {
    /// Creates an index from the given points
    ///
    /// # Arguments
    ///
    /// * `points` - Input points reader
    /// * `node_size` - Size of the KD-tree node, 64 by default. Higher means faster indexing but slower search, and vise versa
    pub fn create<R: PointReader>(points: R, node_size: u8) -> KDBush {
        let mut kdbush = KDBush {
            ids: Vec::with_capacity(points.size_hint()),
            points: Vec::with_capacity(points.size_hint()),
            node_size: node_size,
        };
        points.visit_all(|id, x, y| {
            kdbush.points.push([x, y]);
            kdbush.ids.push(id);
        });
        let size = kdbush.points.len();
        kdbush.sort_kd(0, size - 1, 0);
        kdbush
    }

    /// Creates an empty index
    ///
    /// # Arguments
    ///
    /// * `size_hint` - Number of points to add (maybe 0, if unknown).
    /// * `node_size` - Size of the KD-tree node.
    pub fn new(size_hint: usize, node_size: u8) -> KDBush {
        KDBush {
            ids: Vec::with_capacity(size_hint),
            points: Vec::with_capacity(size_hint),
            node_size: node_size,
        }
    }

    /// Returns the number of stored IDs
    pub fn len(&self) -> usize {
        self.ids.len()
    }

    pub fn is_empty(&self) -> bool {
        self.ids.is_empty()
    }

    /// Add point to index
    pub fn add_point(&mut self, id: usize, x: f64, y: f64) {
        self.points.push([x, y]);
        self.ids.push(id);
    }

    /// Build index
    pub fn build_index(&mut self) {
        let size = self.points.len();
        if size > 0 {
            self.sort_kd(0, size - 1, 0);
        }
    }

    /// Finds all items within the given bounding box
    ///
    /// # Arguments
    ///
    /// * `minx`, `miny`, `maxx`, `maxy` - Bounding box
    /// * `visitor` - Result reader
    pub fn range<F>(
        &self,
        minx: TNumber,
        miny: TNumber,
        maxx: TNumber,
        maxy: TNumber,
        mut visitor: F,
    ) where
        F: FnMut(TIndex),
    {
        if self.is_empty() {
            return;
        }

        self.range_idx(
            minx,
            miny,
            maxx,
            maxy,
            &mut visitor,
            0,
            self.ids.len() - 1,
            0,
        );
    }

    /// Finds items within the given bounding box but stops going deeper down the tree when the visitor returns false.
    ///
    /// # Arguments
    ///
    /// * `minx`, `miny`, `maxx`, `maxy` - Bounding box
    /// * `visitor` - Result reader
    pub fn range_with_predicate<F>(
        &self,
        minx: TNumber,
        miny: TNumber,
        maxx: TNumber,
        maxy: TNumber,
        mut visitor: F,
    ) where
        F: FnMut(TIndex) -> bool,
    {
        if self.is_empty() {
            return;
        }

        self.range_idx_with_predicate(
            minx,
            miny,
            maxx,
            maxy,
            &mut visitor,
            0,
            self.ids.len() - 1,
            0,
        );
    }

    /// Finds all items within a given radius from the query point
    ///
    /// # Arguments
    ///
    /// * `qx`, `qy` - Query point
    /// * `r` - Radius
    /// * `visitor` - Result reader
    pub fn within<F>(&self, qx: TNumber, qy: TNumber, r: TNumber, mut visitor: F)
    where
        F: FnMut(TIndex),
    {
        if self.is_empty() {
            return;
        }

        self.within_idx(qx, qy, r, &mut visitor, 0, self.ids.len() - 1, 0);
    }

    fn range_idx<F>(
        &self,
        minx: TNumber,
        miny: TNumber,
        maxx: TNumber,
        maxy: TNumber,
        visitor: &mut F,
        left: TIndex,
        right: TIndex,
        axis: usize,
    ) where
        F: FnMut(TIndex),
    {
        if right - left <= self.node_size as usize {
            for i in left..right + 1 {
                let x = self.points[i][0];
                let y = self.points[i][1];
                if x >= minx && x <= maxx && y >= miny && y <= maxy {
                    visitor(self.ids[i]);
                }
            }
            return;
        }

        let m = (left + right) >> 1;
        let x = self.points[m][0];
        let y = self.points[m][1];

        if x >= minx && x <= maxx && y >= miny && y <= maxy {
            visitor(self.ids[m]);
        }

        let lte = if axis == 0 { minx <= x } else { miny <= y };
        if lte {
            self.range_idx(minx, miny, maxx, maxy, visitor, left, m - 1, (axis + 1) % 2);
        }

        let gte = if axis == 0 { maxx >= x } else { maxy >= y };
        if gte {
            self.range_idx(
                minx,
                miny,
                maxx,
                maxy,
                visitor,
                m + 1,
                right,
                (axis + 1) % 2,
            );
        }
    }

    fn range_idx_with_predicate<F>(
        &self,
        minx: TNumber,
        miny: TNumber,
        maxx: TNumber,
        maxy: TNumber,
        visitor: &mut F,
        left: TIndex,
        right: TIndex,
        axis: usize,
    ) where
        F: FnMut(TIndex) -> bool,
    {
        if right - left <= self.node_size as usize {
            for i in left..right + 1 {
                let x = self.points[i][0];
                let y = self.points[i][1];
                if x >= minx && x <= maxx && y >= miny && y <= maxy {
                    if !visitor(self.ids[i]) {
                        return;
                    }
                }
            }
            return;
        }

        let m = (left + right) >> 1;
        let x = self.points[m][0];
        let y = self.points[m][1];

        if x >= minx && x <= maxx && y >= miny && y <= maxy {
            if !visitor(self.ids[m]) {
                return;
            }
        }

        let lte = if axis == 0 { minx <= x } else { miny <= y };
        if lte {
            self.range_idx_with_predicate(
                minx,
                miny,
                maxx,
                maxy,
                visitor,
                left,
                m - 1,
                (axis + 1) % 2,
            );
        }

        let gte = if axis == 0 { maxx >= x } else { maxy >= y };
        if gte {
            self.range_idx_with_predicate(
                minx,
                miny,
                maxx,
                maxy,
                visitor,
                m + 1,
                right,
                (axis + 1) % 2,
            );
        }
    }

    fn within_idx<F>(
        &self,
        qx: TNumber,
        qy: TNumber,
        r: TNumber,
        visitor: &mut F,
        left: TIndex,
        right: TIndex,
        axis: usize,
    ) where
        F: FnMut(TIndex),
    {
        let r2 = r * r;

        if right - left <= self.node_size as usize {
            for i in left..right + 1 {
                let x = self.points[i][0];
                let y = self.points[i][1];
                if KDBush::sq_dist(x, y, qx, qy) <= r2 {
                    visitor(self.ids[i]);
                }
            }
            return;
        }

        let m = (left + right) >> 1;
        let x = self.points[m][0];
        let y = self.points[m][1];

        if KDBush::sq_dist(x, y, qx, qy) <= r2 {
            visitor(self.ids[m]);
        }

        let lte = if axis == 0 { qx - r <= x } else { qy - r <= y };
        if lte {
            self.within_idx(qx, qy, r, visitor, left, m - 1, (axis + 1) % 2);
        }

        let gte = if axis == 0 { qx + r >= x } else { qy + r >= y };
        if gte {
            self.within_idx(qx, qy, r, visitor, m + 1, right, (axis + 1) % 2);
        }
    }

    fn sort_kd(&mut self, left: TIndex, right: TIndex, axis: u8) {
        if right - left <= self.node_size as usize {
            return;
        }
        let m: TIndex = (left + right) >> 1;
        if axis == 0 {
            self.select(m, left, right, 0);
        } else {
            self.select(m, left, right, 1);
        }
        self.sort_kd(left, m - 1, (axis + 1) % 2);
        self.sort_kd(m + 1, right, (axis + 1) % 2);
    }

    fn select(&mut self, k: TIndex, mut left: TIndex, mut right: TIndex, axis: usize) {
        while right > left {
            if right - left > 600 {
                let n = (right - left + 1) as f64;
                let m = (k - left + 1) as f64;
                let z = f64::ln(n);
                let s = 0.5 * f64::exp(2.0 * z / 3.0);
                let r = k as f64 - m * s / n
                    + 0.5
                        * f64::sqrt(z * s * (1.0 - s / n))
                        * (if 2.0 * m < n { -1.0 } else { 1.0 });
                self.select(
                    k,
                    cmp::max(left, r as usize),
                    cmp::min(right, (r + s) as usize),
                    axis,
                );
            }

            let t = self.points[k][axis];
            let mut i = left;
            let mut j = right;

            self.swap_item(left, k);
            if self.points[right][axis] > t {
                self.swap_item(left, right);
            }

            while i < j {
                self.swap_item(i, j);
                i += 1;
                j -= 1;
                while self.points[i][axis] < t {
                    i += 1;
                }
                while self.points[j][axis] > t {
                    j -= 1;
                }
            }

            if self.points[left][axis] == t {
                self.swap_item(left, j);
            } else {
                j += 1;
                self.swap_item(j, right);
            }

            if j <= k {
                left = j + 1;
            }
            if k <= j {
                right = j - 1;
            }
        }
    }

    fn swap_item(&mut self, i: TIndex, j: TIndex) {
        self.ids.swap(i, j);
        self.points.swap(i, j);
    }

    fn sq_dist(ax: TNumber, ay: TNumber, bx: TNumber, by: TNumber) -> TNumber {
        (ax - bx).powi(2) + (ay - by).powi(2)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[cfg_attr(rustfmt, rustfmt_skip)]
    const POINTS: [Point; 100] = [
        [54.0,  1.0], [97.0, 21.0], [65.0, 35.0], [33.0, 54.0], [95.0, 39.0], [54.0,  3.0], [53.0, 54.0], [84.0, 72.0],
        [33.0, 34.0], [43.0, 15.0], [52.0, 83.0], [81.0, 23.0], [ 1.0, 61.0], [38.0, 74.0], [11.0, 91.0], [24.0, 56.0],
        [90.0, 31.0], [25.0, 57.0], [46.0, 61.0], [29.0, 69.0], [49.0, 60.0], [ 4.0, 98.0], [71.0, 15.0], [60.0, 25.0],
        [38.0, 84.0], [52.0, 38.0], [94.0, 51.0], [13.0, 25.0], [77.0, 73.0], [88.0, 87.0], [ 6.0, 27.0], [58.0, 22.0],
        [53.0, 28.0], [27.0, 91.0], [96.0, 98.0], [93.0, 14.0], [22.0, 93.0], [45.0, 94.0], [18.0, 28.0], [35.0, 15.0],
        [19.0, 81.0], [20.0, 81.0], [67.0, 53.0], [43.0,  3.0], [47.0, 66.0], [48.0, 34.0], [46.0, 12.0], [32.0, 38.0],
        [43.0, 12.0], [39.0, 94.0], [88.0, 62.0], [66.0, 14.0], [84.0, 30.0], [72.0, 81.0], [41.0, 92.0], [26.0,  4.0],
        [ 6.0, 76.0], [47.0, 21.0], [57.0, 70.0], [71.0, 82.0], [50.0, 68.0], [96.0, 18.0], [40.0, 31.0], [78.0, 53.0],
        [71.0, 90.0], [32.0, 14.0], [55.0,  6.0], [32.0, 88.0], [62.0, 32.0], [21.0, 67.0], [73.0, 81.0], [44.0, 64.0],
        [29.0, 50.0], [70.0,  5.0], [ 6.0, 22.0], [68.0,  3.0], [11.0, 23.0], [20.0, 42.0], [21.0, 73.0], [63.0, 86.0],
        [ 9.0, 40.0], [99.0,  2.0], [99.0, 76.0], [56.0, 77.0], [83.0,  6.0], [21.0, 72.0], [78.0, 30.0], [75.0, 53.0],
        [41.0, 11.0], [95.0, 20.0], [30.0, 38.0], [96.0, 82.0], [65.0, 48.0], [33.0, 18.0], [87.0, 28.0], [10.0, 10.0],
        [40.0, 34.0], [10.0, 20.0], [47.0, 29.0], [46.0, 78.0]
    ];

    impl PointReader for [Point; 100] {
        fn size_hint(&self) -> usize {
            self.len()
        }
        fn visit_all<F>(&self, mut visitor: F)
        where
            F: FnMut(usize, f64, f64),
        {
            for (i, point) in self.iter().enumerate() {
                visitor(i, point[0], point[1]);
            }
        }
    }

    #[test]
    fn test_range() {
        let index = KDBush::create(POINTS, 10);
        let expected_ids = vec![
            3, 90, 77, 72, 62, 96, 47, 8, 17, 15, 69, 71, 44, 19, 18, 45, 60, 20,
        ];
        let mut result = Vec::new();
        index.range(20.0, 30.0, 50.0, 70.0, |idx| result.push(idx));
        assert_eq!(expected_ids, result);
    }

    #[test]
    fn test_range_with_predicate() {
        let index = KDBush::create(POINTS, 10);
        let expected_ids = vec![3, 90, 77, 72, 62, 17, 45, 60];
        let mut result = Vec::new();
        index.range_with_predicate(20.0, 30.0, 50.0, 70.0, |idx| {
            result.push(idx);
            result.len() < 5
        });
        assert_eq!(expected_ids, result);
    }

    #[test]
    fn test_radius() {
        let index = KDBush::create(POINTS, 10);
        let expected_ids = vec![3, 96, 71, 44, 18, 45, 60, 6, 25, 92, 42, 20];
        let mut result = Vec::new();
        index.within(50.0, 50.0, 20.0, |idx| result.push(idx));
        assert_eq!(expected_ids, result);
    }

    #[test]
    fn test_push_api() {
        let mut index = KDBush::new(POINTS.len(), 10);
        for (i, point) in POINTS.iter().enumerate() {
            index.add_point(i, point[0], point[1]);
        }
        index.build_index();
        let expected_ids = vec![
            3, 90, 77, 72, 62, 96, 47, 8, 17, 15, 69, 71, 44, 19, 18, 45, 60, 20,
        ];
        let mut result = Vec::new();
        index.range(20.0, 30.0, 50.0, 70.0, |idx| result.push(idx));
        assert_eq!(expected_ids, result);
    }

    #[test]
    fn test_readme() {
        let points = vec![(54.0, 1.0), (97.0, 21.0), (65.0, 35.0)];
        let index = KDBush::create(points, DEFAULT_NODE_SIZE);
        index.range(20.0, 30.0, 50.0, 70.0, |id| print!("{} ", id));
        index.within(50.0, 50.0, 20.0, |id| print!("{} ", id));
    }
}
