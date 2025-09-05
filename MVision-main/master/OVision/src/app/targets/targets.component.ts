import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { GetTargetService } from './get-targets.service';
import { GetMapService } from '../passive/get-maps.service';
import { Location, Person } from 'src/shared/models/Entities';

@Component({
  selector: 'app-targets',
  templateUrl: './targets.component.html',
  styleUrls: ['./targets.component.sass']
})
export class TargetComponent implements OnInit {
  persons: Person[] = [];
  locations: Location[] = []
  currentPage: number = 1;
  itemsPerPage: number = 4;
  maxLength: number = 1;
  constructor(private cdr: ChangeDetectorRef,
    private getTargetService: GetTargetService,
    private mapService: GetMapService) { }

  ngOnInit() {
    console.log("Updating pages")
    this.fetchTargetCount();
    this.fetchTargets();
  } 

  onPageChange(newPage: number) {
    this.currentPage = newPage;
    console.log(this.currentPage)
    this.fetchTargets();
  }

  fetchTargetCount(){
    this.mapService.fetchCountMap().subscribe(countMaps => {
      console.log(countMaps);
      console.log(countMaps[0])
      const countMap = countMaps[0]?.get_count_map;
      if (countMap) {
        this.maxLength = countMap['target_count'];
        this.cdr.detectChanges();
      } else {
        console.log('Count not retrieved');
      }
    });
  }
  

  fetchTargets() {
    console.log("Fetching Targets");
    this.getTargetService.getTargetService(this.itemsPerPage, this.currentPage).subscribe({
      next: (data: any[]) => {
        console.log("Fetched data:", data);

        this.persons = [];
        this.locations = [];
        data.flatMap(item => item.get_latest_targets).forEach(target => {
        if(target){
            if (target.dob !== null) {
              console.log(target.target_id)
              this.persons.push(new Person(
                target.target_id,
                target.target_name,
                target.alt_name,
                new Date(target.creation_date),
                target.status_value,
                new Date(target.dob),
                target.role
              ));
            } 
            else {
              this.locations.push(new Location(
                target.target_id,
                target.target_name,
                target.alt_name,
                new Date(target.creation_date),
                target.status_value,
                target.access
              ));
            }
          }
        });
      },
      error: (error) => console.error('Error fetching targets:', error)
    });
  }

}
